"""
LoRA Fine-Tuning Execution Engine
Implements PEFT LoRA training on Qwen2.5-Coder-3B-Instruct for Text-to-SQL.
Optimized for NVIDIA RTX 4060 8GB VRAM with gradient checkpointing and batch size 1.
"""

import os
import json
import time
import math
import gc
from typing import Dict, Any, Optional, Callable
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    TrainerCallback
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset

from backend.finetuning.training_config import LoRATrainingConfig


class TrainingProgressCallback(TrainerCallback):
    """Monitors training loss, validation loss, and step progression."""

    def __init__(self, job_state: Dict[str, Any], total_steps: int):
        self.job_state = job_state
        self.total_steps = total_steps
        self.start_time = time.time()

    def on_step_end(self, args, state, control, **kwargs):
        step = state.global_step
        self.job_state["current_step"] = step
        self.job_state["progress_percentage"] = round((step / max(1, self.total_steps)) * 100, 1)

        elapsed = time.time() - self.start_time
        self.job_state["elapsed_time_seconds"] = round(elapsed, 1)

        if step > 0:
            rate = step / elapsed
            remaining_steps = max(0, self.total_steps - step)
            self.job_state["eta_seconds"] = round(remaining_steps / max(1e-5, rate), 1)

        # Record latest training loss if logged
        if state.log_history:
            latest = state.log_history[-1]
            if "loss" in latest:
                self.job_state["current_train_loss"] = round(latest["loss"], 4)
                # Keep loss history point
                if not any(p["step"] == step for p in self.job_state["loss_history"]):
                    self.job_state["loss_history"].append({
                        "step": step,
                        "loss": round(latest["loss"], 4),
                        "epoch": round(state.epoch, 2) if state.epoch else 0.0
                    })

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        if "eval_loss" in metrics:
            val_loss = round(metrics["eval_loss"], 4)
            self.job_state["current_val_loss"] = val_loss
            self.job_state["val_loss_history"].append({
                "step": state.global_step,
                "val_loss": val_loss
            })


class LoRATrainer:
    """Manages pre-flight checks, dataset tokenization, parameter counting, and training."""

    def __init__(self, config: Optional[LoRATrainingConfig] = None):
        self.config = config or LoRATrainingConfig()

    def preflight_check(self) -> Dict[str, Any]:
        """Verify GPU capability, memory, and dataset existence before training."""
        issues = []
        warnings = []

        if not torch.cuda.is_available():
            issues.append("No CUDA GPU detected. RTX 4060 GPU is required for local LoRA training.")
            device_name = "CPU"
            vram_gb = 0.0
        else:
            device_name = torch.cuda.get_device_name(0)
            vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
            if vram_gb < 6.0:
                issues.append(f"Available VRAM ({vram_gb} GB) is below the minimum required 6.0 GB.")

        if not os.path.exists(self.config.train_data_path):
            issues.append(f"Training dataset not found at '{self.config.train_data_path}'. Run dataset preparation first.")

        can_train = (len(issues) == 0)

        return {
            "can_train": can_train,
            "device_name": device_name,
            "vram_gb": vram_gb,
            "estimated_vram_needed_gb": 6.8,
            "issues": issues,
            "warnings": warnings,
            "config": self.config.model_dump()
        }

    def inspect_model_parameters(self) -> Dict[str, Any]:
        """Calculates trainable parameters, total parameters, and percentage for current LoRA config."""
        print("Calculating model parameter statistics for LoRA...")
        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name, trust_remote_code=True)
        # Load meta/empty or light to count parameters
        model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True
        )

        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
            bias="none"
        )

        peft_model = get_peft_model(model, peft_config)
        trainable_params, all_params = peft_model.get_nb_trainable_parameters()
        trainable_pct = round((trainable_params / all_params) * 100, 4)

        del model, peft_model
        gc.collect()

        return {
            "base_model": self.config.base_model_name,
            "lora_rank": self.config.lora_rank,
            "lora_alpha": self.config.lora_alpha,
            "target_modules": self.config.target_modules,
            "trainable_parameters": trainable_params,
            "total_parameters": all_params,
            "trainable_percentage": trainable_pct
        }

    def run_training(self, job_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes supervised LoRA fine-tuning.
        Updates job_state in-place for live monitoring.
        """
        if job_state is None:
            job_state = {}

        job_state["status"] = "INITIALIZING"
        job_state["current_step"] = 0
        job_state["total_steps"] = self.config.max_steps
        job_state["progress_percentage"] = 0.0
        job_state["loss_history"] = []
        job_state["val_loss_history"] = []
        job_state["error"] = None

        preflight = self.preflight_check()
        if not preflight["can_train"]:
            job_state["status"] = "FAILED"
            job_state["error"] = "; ".join(preflight["issues"])
            return job_state

        target_adapter_dir = os.path.join(self.config.output_dir, self.config.adapter_name)
        os.makedirs(target_adapter_dir, exist_ok=True)

        try:
            job_state["status"] = "LOADING_MODEL"
            print(f"Loading base model {self.config.base_model_name}...")

            tokenizer = AutoTokenizer.from_pretrained(
                self.config.base_model_name,
                trust_remote_code=True
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float16

            model = AutoModelForCausalLM.from_pretrained(
                self.config.base_model_name,
                torch_dtype=dtype,
                device_map="auto",
                trust_remote_code=True
            )

            # Gradient checkpointing for 8GB VRAM constraint
            if self.config.gradient_checkpointing:
                model.gradient_checkpointing_enable()
                model.enable_input_require_grads()
                model.config.use_cache = False

            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=self.config.target_modules,
                bias="none"
            )

            peft_model = get_peft_model(model, peft_config)
            trainable_params, all_params = peft_model.get_nb_trainable_parameters()
            trainable_pct = round((trainable_params / all_params) * 100, 4)

            job_state["param_stats"] = {
                "trainable": trainable_params,
                "total": all_params,
                "percentage": trainable_pct
            }

            # Load and tokenize training and validation datasets
            job_state["status"] = "PREPARING_DATA"
            with open(self.config.train_data_path, "r", encoding="utf-8") as f:
                train_raw = json.load(f)
            with open(self.config.val_data_path, "r", encoding="utf-8") as f:
                val_raw = json.load(f)

            def format_and_tokenize(examples_list):
                input_ids_list = []
                labels_list = []

                for ex in examples_list:
                    # SFT Instruction format
                    prompt = (
                        f"<|im_start|>system\nYou are an expert SQL engineer. Given a database schema and a question, generate ONLY an executable SQLite query.<|im_end|>\n"
                        f"<|im_start|>user\n{ex['instruction']}<|im_end|>\n"
                        f"<|im_start|>assistant\n"
                    )
                    target = f"{ex['output']}<|im_end|>"

                    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
                    target_ids = tokenizer.encode(target, add_special_tokens=False)

                    combined_input_ids = prompt_ids + target_ids
                    # Mask prompt tokens so loss is only calculated on the SQL query output
                    combined_labels = [-100] * len(prompt_ids) + target_ids

                    if len(combined_input_ids) > self.config.max_seq_length:
                        combined_input_ids = combined_input_ids[:self.config.max_seq_length]
                        combined_labels = combined_labels[:self.config.max_seq_length]

                    input_ids_list.append(combined_input_ids)
                    labels_list.append(combined_labels)

                return Dataset.from_dict({"input_ids": input_ids_list, "labels": labels_list})

            train_dataset = format_and_tokenize(train_raw[:self.config.max_steps * self.config.gradient_accumulation_steps])
            val_dataset = format_and_tokenize(val_raw[:40])

            data_collator = DataCollatorForSeq2Seq(
                tokenizer=tokenizer,
                pad_to_multiple_of=8,
                return_tensors="pt",
                padding=True
            )

            training_args = TrainingArguments(
                output_dir="outputs/checkpoints",
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=1,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                max_steps=self.config.max_steps,
                logging_steps=self.config.logging_steps,
                eval_strategy="steps",
                eval_steps=self.config.eval_steps,
                save_strategy="no",
                fp16=self.config.fp16,
                optim=self.config.optimizer,
                report_to="none",
                remove_unused_columns=False
            )

            progress_cb = TrainingProgressCallback(job_state, total_steps=self.config.max_steps)

            trainer = Trainer(
                model=peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                data_collator=data_collator,
                callbacks=[progress_cb]
            )

            job_state["status"] = "TRAINING"
            start_train_time = time.time()
            train_result = trainer.train()
            train_duration = round(time.time() - start_train_time, 2)

            # Save the trained LoRA adapter
            job_state["status"] = "SAVING_ADAPTER"
            peft_model.save_pretrained(target_adapter_dir)
            tokenizer.save_pretrained(target_adapter_dir)

            report = {
                "adapter_name": self.config.adapter_name,
                "adapter_dir": target_adapter_dir,
                "base_model": self.config.base_model_name,
                "train_duration_seconds": train_duration,
                "train_loss": train_result.training_loss,
                "steps": self.config.max_steps,
                "param_stats": job_state.get("param_stats"),
                "config": self.config.model_dump()
            }

            with open(os.path.join(target_adapter_dir, "training_summary.json"), "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

            job_state["status"] = "COMPLETED"
            job_state["adapter_path"] = target_adapter_dir
            job_state["summary"] = report

            del trainer, peft_model, model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

            return job_state

        except Exception as e:
            job_state["status"] = "FAILED"
            job_state["error"] = str(e)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            return job_state

