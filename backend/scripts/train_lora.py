#!/usr/bin/env python3
"""
LoRA/QLoRA training script.
Invoked by training_runner.py as a subprocess.
Usage: python3 train_lora.py <path/to/config.json>
"""

import json
import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: train_lora.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = json.loads(config_path.read_text())
    work_dir = config_path.parent
    result_path = work_dir / "result.json"

    try:
        base_model_path = config["base_model"]
        method = config.get("method", "lora")
        output_dir = config["output_dir"]
        dataset_path = config.get("dataset_path", "")
        learning_rate = float(config.get("learning_rate", 2e-4))
        num_epochs = int(config.get("num_epochs", 3))
        batch_size = int(config.get("batch_size", 4))
        lora_r = int(config.get("lora_r", 8))
        lora_alpha = int(config.get("lora_alpha", 32))
        max_length = int(config.get("max_length", 512))

        print(f"[train_lora] Starting training...")
        print(f"  Base model: {base_model_path}")
        print(f"  Method: {method}")
        print(f"  Output: {output_dir}")

        import torch
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForSeq2Seq,
        )
        from peft import LoraConfig, get_peft_model
        from datasets import load_dataset

        print("[train_lora] Loading model...")
        kwargs = {"torch_dtype": torch.bfloat16, "device_map": "auto"}
        model = AutoModelForCausalLM.from_pretrained(base_model_path, **kwargs)
        tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
        lora_config = LoraConfig(
            r=lora_r, lora_alpha=lora_alpha, target_modules=target_modules,
            lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        if dataset_path:
            print(f"[train_lora] Loading dataset from {dataset_path}")
            dataset = load_dataset("json", data_files=dataset_path, split="train")
            def tokenize_fn(examples):
                texts = examples.get("text", examples.get("instruction", [""]))
                if isinstance(texts, str):
                    texts = [texts]
                model_inputs = tokenizer(texts, truncation=True, max_length=max_length, padding=False)
                model_inputs["labels"] = model_inputs["input_ids"].copy()
                return model_inputs
            tokenized = dataset.map(tokenize_fn, remove_columns=dataset.column_names)
            data_collator = DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8)
        else:
            print("[train_lora] No dataset provided, using dummy data")
            dummy = tokenizer(["Hello world"] * 10, truncation=True, max_length=max_length, padding=False)
            dummy["labels"] = dummy["input_ids"].copy()
            tokenized = dummy
            data_collator = None

        training_args = TrainingArguments(
            output_dir=output_dir, per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4, num_train_epochs=num_epochs,
            learning_rate=learning_rate, bf16=torch.cuda.is_available(),
            logging_steps=10, save_strategy="epoch", save_total_limit=2,
            remove_unused_columns=False, report_to="none",
        )

        trainer = Trainer(
            model=model, args=training_args, train_dataset=tokenized,
            data_collator=data_collator, tokenizer=tokenizer,
        )
        print("[train_lora] Starting training loop...")
        trainer.train()

        print(f"[train_lora] Saving model to {output_dir}")
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)

        result = {
            "status": "completed",
            "output_path": output_dir,
            "metrics": {"train_loss": float(trainer.state.log_history[-1].get("loss", 0)) if trainer.state.log_history else 0},
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[train_lora] Training completed.")

    except Exception as e:
        print(f"[train_lora] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        result = {"status": "failed", "error": str(e)}
        result_path.write_text(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
