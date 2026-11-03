"""
Model Comparison Service
Executes a single database schema and question against all three techniques side-by-side:
1. NVIDIA Nemotron 3.5 Lightning
2. Local Qwen2.5-Coder-3B-Instruct (Few-Shot)
3. Local Qwen2.5-Coder-3B-Instruct (LoRA Fine-Tuned)
"""

import time
from typing import Dict, Any, Optional

from backend.database.db_manager import DatabaseManager
from backend.database.schema_extractor import DatabaseSchemaExtractor
from backend.models.nemotron_api import NemotronSQLGenerator
from backend.models.qwen_model import LocalQwenEngine
from backend.database.sql_validator import SafeSQLExecutor, SQLSecurityValidator, SQLValidationError


class ModelComparisonService:
    """Runs a side-by-side comparison across all supported models on a user input."""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.nemotron = NemotronSQLGenerator()
        self.qwen_engine = LocalQwenEngine.get_instance()

    def compare(
        self,
        database_id: str,
        question: str,
        num_few_shot_examples: int = 3,
        adapter_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes query against all 3 model variations and safely executes each generated SQL.
        """
        db_path = self.db_manager.get_database_path(database_id)
        extractor = DatabaseSchemaExtractor(db_path)
        schema_data = extractor.extract_full_schema()
        schema_text = schema_data["formatted_text"]
        allowed_tables = list(schema_data["tables"].keys())
        executor = SafeSQLExecutor(db_path=db_path)

        results = {}

        # 1. NVIDIA Nemotron Lightning
        start_n = time.time()
        nem_res = self.nemotron.generate_sql(schema_text, question)
        nem_sql = nem_res.get("sql", "")
        nem_valid = False
        nem_val_err = None
        nem_exec = None

        if nem_res.get("success") and nem_sql:
            try:
                nem_clean, _ = SQLSecurityValidator.validate_sql(nem_sql, allowed_tables=allowed_tables)
                nem_valid = True
                nem_exec = executor.execute(nem_clean, validate=False)
            except SQLValidationError as ve:
                nem_val_err = str(ve)

        results["nemotron"] = {
            "name": "NVIDIA Nemotron 3.5 Lightning",
            "model_id": "nvidia/nemotron-3.5-lightning-30b-a3b",
            "technique": "API Direct Inference (Thinking Disabled)",
            "sql": nem_sql,
            "raw_response": nem_res.get("raw_response", ""),
            "latency_ms": nem_res.get("latency_ms", round((time.time() - start_n) * 1000, 2)),
            "is_valid": nem_valid,
            "validation_error": nem_val_err,
            "execution": nem_exec,
            "error": nem_res.get("error")
        }

        # 2. Local Qwen Few-Shot
        start_qf = time.time()
        qf_res = self.qwen_engine.generate_sql(
            schema_text=schema_text,
            question=question,
            mode="few_shot",
            num_few_shot_examples=num_few_shot_examples
        )
        qf_sql = qf_res.get("sql", "")
        qf_valid = False
        qf_val_err = None
        qf_exec = None

        if qf_res.get("success") and qf_sql:
            try:
                qf_clean, _ = SQLSecurityValidator.validate_sql(qf_sql, allowed_tables=allowed_tables)
                qf_valid = True
                qf_exec = executor.execute(qf_clean, validate=False)
            except SQLValidationError as ve:
                qf_val_err = str(ve)

        results["qwen_few_shot"] = {
            "name": "Local Qwen2.5-Coder-3B-Instruct",
            "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct",
            "technique": f"In-Context Few-Shot ({num_few_shot_examples} Spider Demonstrations)",
            "sql": qf_sql,
            "raw_response": qf_res.get("raw_response", ""),
            "latency_ms": qf_res.get("latency_ms", round((time.time() - start_qf) * 1000, 2)),
            "is_valid": qf_valid,
            "validation_error": qf_val_err,
            "execution": qf_exec,
            "error": qf_res.get("error")
        }

        # 3. Local Qwen LoRA Fine-Tuned
        start_ql = time.time()
        ql_res = self.qwen_engine.generate_sql(
            schema_text=schema_text,
            question=question,
            mode="lora",
            adapter_name=adapter_name
        )
        ql_sql = ql_res.get("sql", "")
        ql_valid = False
        ql_val_err = None
        ql_exec = None

        if ql_res.get("success") and ql_sql:
            try:
                ql_clean, _ = SQLSecurityValidator.validate_sql(ql_sql, allowed_tables=allowed_tables)
                ql_valid = True
                ql_exec = executor.execute(ql_clean, validate=False)
            except SQLValidationError as ve:
                ql_val_err = str(ve)

        results["qwen_lora"] = {
            "name": "Local Qwen2.5-Coder-3B-Instruct + LoRA",
            "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct (Adapter)",
            "technique": "Supervised LoRA Fine-Tuned Adapter",
            "sql": ql_sql,
            "raw_response": ql_res.get("raw_response", ""),
            "latency_ms": ql_res.get("latency_ms", round((time.time() - start_ql) * 1000, 2)),
            "is_valid": ql_valid,
            "validation_error": ql_val_err,
            "execution": ql_exec,
            "error": ql_res.get("error")
        }

        return {
            "question": question,
            "database_id": database_id,
            "models": results
        }

