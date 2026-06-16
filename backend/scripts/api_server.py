#!/usr/bin/env python3
"""
Inference server for published models.
Provides OpenAI-compatible chat completion and embedding endpoints.
Usage: python3 api_server.py --model_path <path> --model_type <llm|embedding> --host <host> --port <port>
"""

import argparse
import json
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AIStudio Inference Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_model = None
_tokenizer = None
_model_type = None


class ChatRequest(BaseModel):
    model: str = ""
    messages: list[dict]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9


class EmbeddingRequest(BaseModel):
    model: str = ""
    input: list[str]


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if _model_type != "llm":
        raise HTTPException(400, "Model is not an LLM")

    prompt_parts = []
    for msg in req.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    prompt_parts.append("Assistant: ")
    prompt = "\n".join(prompt_parts)

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    outputs = _model.generate(
        **inputs, max_new_tokens=req.max_tokens, temperature=req.temperature,
        top_p=req.top_p, do_sample=req.temperature > 0,
        pad_token_id=_tokenizer.pad_token_id,
    )
    response_text = _tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    return {
        "id": "chatcmpl-1", "object": "chat.completion",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": response_text}, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": inputs.input_ids.shape[1],
            "completion_tokens": outputs.shape[1] - inputs.input_ids.shape[1],
            "total_tokens": outputs.shape[1],
        },
    }


@app.post("/v1/embeddings")
async def embeddings(req: EmbeddingRequest):
    if _model_type not in ("embedding", "llm"):
        raise HTTPException(400, f"Model type '{_model_type}' does not support embeddings")

    import torch
    all_embeddings = []
    for text in req.input:
        inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(_model.device)
        with torch.no_grad():
            outputs = _model(**inputs, output_hidden_states=True)
            last_hidden = outputs.hidden_states[-1] if hasattr(outputs, "hidden_states") else outputs.last_hidden_state
            mask = inputs.attention_mask.unsqueeze(-1).float()
            pooled = (last_hidden * mask).sum(dim=1) / mask.sum(dim=1)
            embedding = pooled[0].cpu().tolist()
            all_embeddings.append(embedding)

    return {
        "model": req.model,
        "data": [{"object": "embedding", "index": i, "embedding": emb} for i, emb in enumerate(all_embeddings)],
        "usage": {"total_tokens": 0},
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _model is not None, "model_type": _model_type}


def main():
    parser = argparse.ArgumentParser(description="AIStudio Inference Server")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--model_type", default="llm", choices=["llm", "embedding"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8300)
    parser.add_argument("--service_id", type=int, default=0)
    args = parser.parse_args()

    global _model, _tokenizer, _model_type
    _model_type = args.model_type

    print(f"[api_server] Loading model from {args.model_path}")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    _model = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=torch.bfloat16, device_map="auto", output_hidden_states=True,
    )
    _tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    _model.eval()
    print(f"[api_server] Model loaded. Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
