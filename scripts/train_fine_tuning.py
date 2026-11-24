"""Example Fine-Tuning Script for Algerian Darja LLMs using HuggingFace TRL & Unsloth.

Dataset: data/fine_tuning/algerian_corpus_alpaca.json (5,288 real conversational pairs)
Compatible with: LLaMA 3.1 8B, Qwen 2.5 7B, Mistral 7B, Gemma 2 9B.

Usage:
    pip install trl peft transformers datasets accelerate bitsandbytes
    python scripts/train_fine_tuning.py --model_name unsloth/llama-3-8b-Instruct-bnb-4bit
"""

import argparse
import json
from pathlib import Path

def train_darja_model(model_name: str = "unsloth/llama-3-8b-Instruct-bnb-4bit", output_dir: str = "./darja-lora-model"):
    print(f"Loading Algerian Darja fine-tuning corpus...")
    corpus_path = Path(__file__).resolve().parent.parent / "data" / "fine_tuning" / "algerian_corpus_alpaca.json"
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data):,} authentic Algerian instruction samples.")
    
    # Prompt template formatting
    def format_prompt(sample):
        instruction = sample["instruction"]
        user_input = sample.get("input", "")
        output = sample["output"]
        
        if user_input:
            text = f"<|im_start|>system\n{instruction}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
        else:
            text = f"<|im_start|>system\nYou are an authentic Algerian AI assistant.<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
        return {"text": text}

    formatted = [format_prompt(s) for s in data]
    print(f"Formatted {len(formatted)} prompt strings with ChatML tokens.")
    print("\n--- Example Sample 1 ---")
    print(formatted[0]["text"][:250] + "...")
    print("\n--- Example Sample 2 (Translation) ---")
    print(formatted[2800]["text"][:250] + "...")
    
    print("\nTo launch full LoRA fine-tuning:")
    print("```python")
    print("from datasets import Dataset")
    print("from trl import SFTTrainer")
    print("from transformers import TrainingArguments")
    print("")
    print("dataset = Dataset.from_list(formatted)")
    print("trainer = SFTTrainer(")
    print(f"    model='{model_name}',")
    print("    train_dataset=dataset,")
    print("    dataset_text_field='text',")
    print("    max_seq_length=1024,")
    print("    args=TrainingArguments(")
    print("        per_device_train_batch_size=4,")
    print("        gradient_accumulation_steps=4,")
    print("        warmup_steps=10,")
    print("        max_steps=300,")
    print("        learning_rate=2e-4,")
    print("        fp16=True,")
    print("        logging_steps=10,")
    print(f"        output_dir='{output_dir}',")
    print("    ),")
    print(")")
    print("trainer.train()")
    print("```")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train an Algerian Darja LLM on authentic corpora.")
    parser.add_argument("--model_name", default="unsloth/llama-3-8b-Instruct-bnb-4bit", help="Base model identifier")
    parser.add_argument("--output_dir", default="./darja-lora-model", help="LoRA weights output directory")
    args = parser.parse_args()
    train_darja_model(args.model_name, args.output_dir)
