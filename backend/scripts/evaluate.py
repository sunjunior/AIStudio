#!/usr/bin/env python3
"""
Evaluation script.
Invoked by evaluator.py as a subprocess.
Usage: python3 evaluate.py <path/to/config.json>
"""

import json
import math
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: evaluate.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = json.loads(config_path.read_text())
    work_dir = config_path.parent
    result_path = work_dir / "result.json"

    try:
        model_path = config["model_path"]
        model_type = config.get("model_type", "llm")
        eval_type = config.get("eval_type", "perplexity")
        dataset = config.get("dataset", "")

        print(f"[evaluate] Starting evaluation...")
        print(f"  Model: {model_path}, Type: {eval_type}")

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print("[evaluate] Loading model...")
        model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model.eval()
        metrics = {}

        if eval_type == "perplexity":
            if dataset:
                from datasets import load_dataset
                data = load_dataset("json", data_files=dataset, split="train")
                texts = data.get("text", data.get("instruction", []))
            else:
                texts = [
                    "The quick brown fox jumps over the lazy dog.",
                    "Machine learning is a subset of artificial intelligence.",
                    "Transformers have revolutionized natural language processing.",
                ]
            encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
            input_ids = encodings.input_ids
            attn_mask = encodings.attention_mask
            max_len = 512
            stride = 256
            nlls = []
            with torch.no_grad():
                for i in range(0, input_ids.size(1), stride):
                    begin_loc = max(i, 0)
                    end_loc = min(i + max_len, input_ids.size(1))
                    if end_loc - begin_loc < 10:
                        break
                    trg_len = end_loc - begin_loc
                    chunk = input_ids[:, begin_loc:end_loc]
                    attn = attn_mask[:, begin_loc:end_loc] if attn_mask is not None else None
                    outputs = model(chunk, attention_mask=attn, labels=chunk)
                    nlls.append(outputs.loss.item() * trg_len)
            if nlls:
                total_weight = sum(
                    min(max_len, input_ids.size(1) - i) if (i + max_len) <= input_ids.size(1) else input_ids.size(1) - i
                    for i in range(0, input_ids.size(1), stride) if (input_ids.size(1) - i) >= 10
                )
                ppl = math.exp(sum(nlls) / total_weight)
                metrics["perplexity"] = round(ppl, 4)
                print(f"[evaluate] Perplexity: {ppl:.4f}")

        elif eval_type == "benchmark":
            if dataset:
                from datasets import load_dataset
                data = load_dataset("json", data_files=dataset, split="train")
                correct = 0
                total = 0
                for item in data:
                    prompt = item.get("question", item.get("text", ""))
                    answer = item.get("answer", item.get("label", ""))
                    if not prompt or not answer:
                        continue
                    inputs = tokenizer(prompt, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model.generate(**inputs, max_new_tokens=20)
                    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    if answer in generated:
                        correct += 1
                    total += 1
                accuracy = correct / total if total > 0 else 0
                metrics["accuracy"] = round(accuracy, 4)
                metrics["total_samples"] = total
                print(f"[evaluate] Accuracy: {accuracy:.4f} ({correct}/{total})")
            else:
                metrics["note"] = "No dataset provided for benchmark"

        elif eval_type == "custom":
            metrics["note"] = "Custom evaluation not implemented - extend evaluate.py"

        result = {"status": "completed", "metrics": metrics}
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[evaluate] Completed. Results: {json.dumps(metrics)}")

    except Exception as e:
        print(f"[evaluate] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        result = {"status": "failed", "error": str(e)}
        result_path.write_text(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
