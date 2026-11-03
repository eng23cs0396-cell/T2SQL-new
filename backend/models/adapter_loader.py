"""
LoRA Adapter Loader and Manager
Scans and validates trained PEFT LoRA adapters in outputs/adapters.
"""

import os
import json
from typing import List, Dict, Any, Optional


class AdapterManager:
    """Manages finding, inspecting, and resolving trained LoRA adapter directories."""

    def __init__(self, adapters_dir: str = "outputs/adapters"):
        self.adapters_dir = os.path.abspath(adapters_dir)
        os.makedirs(self.adapters_dir, exist_ok=True)

    def list_adapters(self) -> List[Dict[str, Any]]:
        """List all valid LoRA adapter checkpoints found in the output directory."""
        adapters = []
        if not os.path.exists(self.adapters_dir):
            return adapters

        for item in os.listdir(self.adapters_dir):
            adapter_path = os.path.join(self.adapters_dir, item)
            config_file = os.path.join(adapter_path, "adapter_config.json")
            if os.path.isdir(adapter_path) and os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    size_mb = sum(
                        os.path.getsize(os.path.join(adapter_path, f))
                        for f in os.listdir(adapter_path)
                        if os.path.isfile(os.path.join(adapter_path, f))
                    ) / (1024 * 1024)

                    adapters.append({
                        "name": item,
                        "path": adapter_path,
                        "rank": config_data.get("r", 8),
                        "alpha": config_data.get("lora_alpha", 16),
                        "dropout": config_data.get("lora_dropout", 0.05),
                        "target_modules": config_data.get("target_modules", []),
                        "base_model": config_data.get("base_model_name_or_path", "Qwen/Qwen2.5-Coder-3B-Instruct"),
                        "size_mb": round(size_mb, 2)
                    })
                except Exception:
                    continue

        return sorted(adapters, key=lambda x: x["name"])

    def get_adapter_path(self, adapter_name: Optional[str] = None) -> Optional[str]:
        """Resolves adapter path. If adapter_name is None, returns the first available or None."""
        if adapter_name:
            path = os.path.join(self.adapters_dir, adapter_name)
            if os.path.exists(os.path.join(path, "adapter_config.json")):
                return path
            return None

        adapters = self.list_adapters()
        if adapters:
            return adapters[0]["path"]
        return None

