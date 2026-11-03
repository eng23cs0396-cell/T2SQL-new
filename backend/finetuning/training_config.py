"""
LoRA Fine-Tuning Configuration Schema
Strictly tailored for NVIDIA RTX 4060 (8GB VRAM) hardware constraints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LoRATrainingConfig(BaseModel):
    """Configuration parameters for LoRA fine-tuning."""

    base_model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct"
    adapter_name: str = "qwen_lora_spider"

    # LoRA hyperparameters
    lora_rank: int = Field(default=8, ge=2, le=64, description="LoRA attention rank")
    lora_alpha: int = Field(default=16, ge=4, le=128, description="LoRA scaling factor")
    lora_dropout: float = Field(default=0.05, ge=0.0, le=0.5, description="LoRA dropout")
    target_modules: List[str] = Field(
        default=["q_proj", "k_proj", "v_proj", "o_proj"],
        description="Linear projection layers targeted for adaptation"
    )

    # Hardware & Memory optimization settings for 8GB VRAM
    batch_size: int = Field(default=1, ge=1, le=4, description="Per-device batch size")
    gradient_accumulation_steps: int = Field(default=4, ge=1, le=16, description="Gradient accumulation steps")
    learning_rate: float = Field(default=2e-4, ge=1e-5, le=1e-3, description="Optimizer learning rate")
    max_seq_length: int = Field(default=512, ge=128, le=1024, description="Maximum sequence length")
    num_train_epochs: int = Field(default=1, ge=1, le=5, description="Number of training epochs")
    max_steps: int = Field(default=50, ge=10, le=1000, description="Max training steps for demonstration/lab")
    warmup_steps: int = Field(default=5, ge=0, le=50)
    logging_steps: int = Field(default=2, ge=1, le=20)
    eval_steps: int = Field(default=10, ge=5, le=50)

    # Precision & gradient checkpointing
    fp16: bool = True
    bf16: bool = False
    gradient_checkpointing: bool = True
    optimizer: str = "adamw_torch"

    # Dataset paths
    train_data_path: str = "data/processed/spider_train.json"
    val_data_path: str = "data/processed/spider_val.json"
    output_dir: str = "outputs/adapters"

