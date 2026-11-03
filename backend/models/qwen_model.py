"""
Local Qwen2.5-Coder-3B-Instruct Inference Engine
Manages model loading, GPU memory, few-shot prompting, and LoRA adapter inference.
Strictly maintains base weights intact and prevents redundant model instances in VRAM.
"""

import os
import gc
import time
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from backend.prompting.few_shot import FewShotPromptManager
from backend.models.adapter_loader import AdapterManager
from backend.database.sql_validator import SQLSecurityValidator


class LocalQwenEngine:
    """Singleton engine for local Qwen2.5-Coder-3B-Instruct model inference."""

    _instance: Optional["LocalQwenEngine"] = None

    MODEL_ID = "Qwen/Qwen2.5-Coder-3B-Instruct"

    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.base_model = None
        self.current_model = None  # Points to base_model or PeftModel
        self.current_adapter: Optional[str] = None
        self.prompt_manager = FewShotPromptManager()
        self.adapter_manager = AdapterManager()

    @classmethod
    def get_instance(cls) -> "LocalQwenEngine":
        if cls._instance is None:
            cls._instance = LocalQwenEngine()
        return cls._instance

    def get_gpu_status(self) -> Dict[str, Any]:
        """Returns GPU VRAM allocation and total capacity in MB."""
        if not torch.cuda.is_available():
            return {
                "cuda_available": False,
                "device_name": "CPU",
                "allocated_mb": 0.0,
                "reserved_mb": 0.0,
                "total_mb": 0.0,
                "free_mb": 0.0
            }

        allocated = torch.cuda.memory_allocated(0) / (1024 * 1024)
        reserved = torch.cuda.memory_reserved(0) / (1024 * 1024)
        total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
        free = total - reserved

        return {
            "cuda_available": True,
            "device_name": torch.cuda.get_device_name(0),
            "allocated_mb": round(allocated, 2),
            "reserved_mb": round(reserved, 2),
            "total_mb": round(total, 2),
            "free_mb": round(free, 2)
        }

    def load_base_model(self):
        """Loads tokenizer and base model into GPU memory if not already loaded."""
        if self.base_model is not None:
            return

        print(f"Loading {self.MODEL_ID} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_ID,
            trust_remote_code=True
        )

        dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float16
        if self.device == "cpu":
            dtype = torch.float32

        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_ID,
            torch_dtype=dtype,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        )

        if self.device != "cuda":
            self.base_model.to(self.device)

        self.base_model.eval()
        self.current_model = self.base_model
        self.current_adapter = None
        print("Base model loaded successfully.")

    def ensure_mode(self, mode: str, adapter_name: Optional[str] = None):
        """
        Ensures model is in 'few_shot' (base) or 'lora' (adapter) mode.
        Reuses base model weights without reloading from disk.
        """
        self.load_base_model()

        if mode == "few_shot":
            # Use base model without adapter
            self.current_model = self.base_model
            self.current_adapter = None
        elif mode == "lora":
            target_path = self.adapter_manager.get_adapter_path(adapter_name)
            if not target_path:
                raise ValueError(
                    f"No trained LoRA adapter found at '{adapter_name or 'outputs/adapters'}'. "
                    "Train an adapter first using the Fine-Tuning Lab or select Few-Shot mode."
                )

            if self.current_adapter != target_path:
                print(f"Attaching LoRA adapter from {target_path}...")
                self.current_model = PeftModel.from_pretrained(
                    self.base_model,
                    target_path,
                    is_trainable=False
                )
                self.current_model.eval()
                self.current_adapter = target_path
                print("LoRA adapter attached.")

    def generate_sql(
        self,
        schema_text: str,
        question: str,
        mode: str = "few_shot",
        num_few_shot_examples: int = 3,
        adapter_name: Optional[str] = None,
        max_new_tokens: int = 256
    ) -> Dict[str, Any]:
        """
        Generates SQL using local Qwen under either few-shot or LoRA adapter mode.
        """
        start_time = time.time()
        try:
            self.ensure_mode(mode=mode, adapter_name=adapter_name)

            if mode == "few_shot":
                prompt_content = self.prompt_manager.build_prompt(
                    schema_text=schema_text,
                    question=question,
                    num_examples=num_few_shot_examples
                )
                messages = [
                    {"role": "system", "content": "You are a professional SQL assistant. Generate ONLY a valid SQLite query for the requested target database."},
                    {"role": "user", "content": prompt_content}
                ]
            else:
                # LoRA inference: uses the exact instruction format used during training
                instruction = f"{schema_text}\n\nQuestion: {question}"
                messages = [
                    {"role": "system", "content": "You are an expert SQL engineer. Given a database schema and a question, generate ONLY an executable SQLite query."},
                    {"role": "user", "content": instruction}
                ]

            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                output_ids = self.current_model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.01,  # near deterministic
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            new_tokens = output_ids[0][inputs.input_ids.shape[1]:]
            raw_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            latency_ms = round((time.time() - start_time) * 1000, 2)

            cleaned_sql = SQLSecurityValidator.clean_sql_string(raw_text)

            return {
                "success": True,
                "sql": cleaned_sql,
                "raw_response": raw_text,
                "latency_ms": latency_ms,
                "mode": mode,
                "adapter": self.current_adapter,
                "output_tokens": len(new_tokens),
                "gpu_status": self.get_gpu_status(),
                "error": None
            }

        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "sql": "",
                "raw_response": "",
                "latency_ms": latency_ms,
                "mode": mode,
                "adapter": None,
                "output_tokens": 0,
                "gpu_status": self.get_gpu_status(),
                "error": str(e)
            }

    def free_memory(self):
        """Free cached GPU memory without unloading base weights."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

