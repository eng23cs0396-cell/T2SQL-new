"""
CLI Runner for LoRA Fine-Tuning Qwen2.5-Coder-3B-Instruct
Runs PEFT fine-tuning with conservative settings for RTX 4060 8GB VRAM.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.finetuning.training_config import LoRATrainingConfig
from backend.finetuning.train_lora import LoRATrainer

def main():
    print("=" * 60)
    print("QueryMind: LoRA Fine-Tuning for Qwen2.5-Coder-3B-Instruct")
    print("Target Hardware: NVIDIA RTX 4060 (8GB VRAM)")
    print("=" * 60)

    config = LoRATrainingConfig(
        base_model_name="Qwen/Qwen2.5-Coder-3B-Instruct",
        adapter_name="qwen_lora_spider",
        lora_rank=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        max_seq_length=512,
        max_steps=30,  # 30 targeted steps for stable demonstration adapter
        logging_steps=2,
        eval_steps=10,
        gradient_checkpointing=True,
        fp16=True
    )

    trainer = LoRATrainer(config)

    print("\n[1/3] Performing Hardware & Memory Preflight Check...")
    preflight = trainer.preflight_check()
    print(f"Device: {preflight['device_name']} | VRAM: {preflight['vram_gb']} GB")
    if not preflight["can_train"]:
        print("Preflight check FAILED:")
        for issue in preflight["issues"]:
            print(f" - {issue}")
        sys.exit(1)
    print("[Preflight OK]")

    print("\n[2/3] Initiating Supervised LoRA Fine-Tuning...")
    job_state = {}
    result = trainer.run_training(job_state)

    if result.get("status") == "COMPLETED":
        print("\n" + "=" * 60)
        print("[3/3] LoRA Fine-Tuning COMPLETED SUCCESSFULLY!")
        print(f"Adapter saved to: {result.get('adapter_path')}")
        print(f"Final Train Loss: {result.get('summary', {}).get('train_loss')}")
        print(f"Train Duration: {result.get('summary', {}).get('train_duration_seconds')} seconds")
        print("=" * 60)
    else:
        print("\nTraining Failed:")
        print(result.get("error"))
        sys.exit(1)

if __name__ == "__main__":
    main()

