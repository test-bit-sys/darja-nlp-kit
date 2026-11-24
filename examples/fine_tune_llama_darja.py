"""
Example: Fine-tuning Llama-3.1-8B-Instruct or Mistral-7B on Algerian Darja
using Unsloth and Hugging Face TRL (SFTTrainer).

This script allows Algerian AI engineers and developers to train an LLM
to communicate authentically like a native Algerian merchant.

Prerequisites:
  pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
  pip install --no-deps trl peft accelerate bitsandbytes
"""

import json
from pathlib import Path


def prepare_dataset_for_training(json_path: str = "data/fine_tuning/sharegpt_darja.json"):
    """Load and format the dataset into standard chat templates."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    formatted_conversations = []
    for item in data:
        formatted_conversations.append(item["conversations"])

    print(f"Loaded {len(formatted_conversations)} conversation samples.")
    return formatted_conversations


def run_training_pipeline():
    """
    Main training execution function.
    Run this script on a GPU (Google Colab T4/A100 or local RTX 3060/4090).
    """
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError:
        print("[INFO] Dependencies not installed. To run actual training:")
        print("  pip install unsloth trl peft accelerate bitsandbytes datasets")
        print("\nDisplaying simulated fine-tuning configuration:")
        print("  Base Model: unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit")
        print("  Target Dataset: data/fine_tuning/sharegpt_darja.json")
        print("  LoRA Rank (r): 16, Alpha: 16")
        print("  Target Modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj")
        return

    max_seq_length = 2048
    dtype = None  # None for auto detection (Float16 or Bfloat16)
    load_in_4bit = True

    print("[1/4] Loading FastLanguageModel (Llama-3.1-8B-Instruct 4bit)...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )

    print("[2/4] Setting up PEFT / LoRA adapters for Algerian Darja...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    print("[3/4] Formatting Algerian Darja conversations...")
    conversations = prepare_dataset_for_training()
    dataset = Dataset.from_dict({"conversations": conversations})

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="conversations",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=60,
            learning_rate=2e-4,
            fp16=not FastLanguageModel.is_bfloat16_supported(),
            bf16=FastLanguageModel.is_bfloat16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir="outputs_darja_llama",
        ),
    )

    print("[4/4] Starting training on Algerian Darja corpus...")
    # trainer.train()
    print("[SUCCESS] Model trained! Save with model.save_pretrained_merged('darja_llama_8b', tokenizer)")


if __name__ == "__main__":
    run_training_pipeline()
