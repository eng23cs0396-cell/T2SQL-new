"""
Common Evaluation Runner
Benchmarks NVIDIA Nemotron Lightning, Qwen Few-Shot, and Qwen LoRA on held-out Spider test instances.
Calculates validity rate, execution accuracy, end-to-end accuracy, latency, and resource metrics.
Exports results to JSON and CSV.
"""

import os
import csv
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.evaluation.test_cases import TestCaseLoader
from backend.evaluation.metrics import SQLResultComparator
from backend.database.sql_validator import SafeSQLExecutor, SQLSecurityValidator, SQLValidationError
from backend.models.nemotron_api import NemotronSQLGenerator
from backend.models.qwen_model import LocalQwenEngine
from backend.database.schema_extractor import DatabaseSchemaExtractor


class ModelEvaluator:
    """Runs rigorous, reproducible evaluation of Text-to-SQL models."""

    def __init__(self, output_dir: str = "outputs/evaluation"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_loader = TestCaseLoader()
        self.nemotron = NemotronSQLGenerator()
        self.qwen_engine = LocalQwenEngine.get_instance()

    def evaluate_model(
        self,
        model_type: str,  # 'nemotron', 'qwen_few_shot', 'qwen_lora'
        test_limit: int = 15,
        adapter_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs evaluation for specified model on held-out test cases.
        """
        cases = self.test_loader.get_test_cases(limit=test_limit)
        if not cases:
            raise ValueError("No held-out test cases available for evaluation.")

        detailed_results = []
        total_cases = len(cases)
        valid_sql_count = 0
        exec_success_count = 0
        exec_accuracy_count = 0
        api_success_count = 0
        total_latency_ms = 0.0

        print(f"Starting evaluation of '{model_type}' on {total_cases} test cases...")

        for idx, case in enumerate(cases, start=1):
            db_path = case["db_path"]
            question = case["question"]
            gold_sql = case["gold_sql"]

            # Dynamic schema extraction for target database
            extractor = DatabaseSchemaExtractor(db_path)
            schema_data = extractor.extract_full_schema()
            schema_text = schema_data["formatted_text"]
            allowed_tables = list(schema_data["tables"].keys())

            # 1. Execute Gold SQL to obtain Ground Truth
            executor = SafeSQLExecutor(db_path=db_path)
            gold_exec = executor.execute(gold_sql, validate=False)
            gold_rows = gold_exec.get("rows", [])

            # 2. Generate Predicted SQL using Model
            start_gen = time.time()
            if model_type == "nemotron":
                gen_res = self.nemotron.generate_sql(schema_text, question)
            elif model_type == "qwen_few_shot":
                gen_res = self.qwen_engine.generate_sql(
                    schema_text=schema_text,
                    question=question,
                    mode="few_shot",
                    num_few_shot_examples=3
                )
            elif model_type == "qwen_lora":
                gen_res = self.qwen_engine.generate_sql(
                    schema_text=schema_text,
                    question=question,
                    mode="lora",
                    adapter_name=adapter_name
                )
            else:
                raise ValueError(f"Unknown model_type: '{model_type}'")

            generation_time_ms = gen_res.get("latency_ms", (time.time() - start_gen) * 1000)
            total_latency_ms += generation_time_ms
            raw_sql = gen_res.get("sql", "")
            model_error = gen_res.get("error")

            is_api_success = (model_error is None and bool(raw_sql))
            if is_api_success:
                api_success_count += 1

            # 3. Validate Generated SQL
            is_valid_sql = False
            validation_error = None
            cleaned_sql = raw_sql
            if is_api_success:
                try:
                    cleaned_sql, _ = SQLSecurityValidator.validate_sql(raw_sql, allowed_tables=allowed_tables)
                    is_valid_sql = True
                    valid_sql_count += 1
                except SQLValidationError as ve:
                    validation_error = str(ve)

            # 4. Execute Predicted SQL
            is_exec_success = False
            is_accurate = False
            pred_exec_error = None
            pred_rows = []

            if is_valid_sql:
                pred_exec = executor.execute(cleaned_sql, validate=False)
                if pred_exec["success"]:
                    is_exec_success = True
                    exec_success_count += 1
                    pred_rows = pred_exec.get("rows", [])

                    # 5. Semantic Result Equivalence (Execution Accuracy)
                    order_sensitive = "order by" in gold_sql.lower()
                    is_accurate = SQLResultComparator.compare_results(
                        pred_rows, gold_rows, order_sensitive=order_sensitive
                    )
                    if is_accurate:
                        exec_accuracy_count += 1
                else:
                    pred_exec_error = pred_exec.get("error")

            detailed_results.append({
                "case_id": case["id"],
                "db_id": case["db_id"],
                "question": question,
                "gold_sql": gold_sql,
                "predicted_sql": cleaned_sql,
                "api_success": is_api_success,
                "valid_sql": is_valid_sql,
                "execution_success": is_exec_success,
                "execution_accuracy": is_accurate,
                "latency_ms": round(generation_time_ms, 2),
                "error": model_error or validation_error or pred_exec_error
            })

        avg_latency = round(total_latency_ms / max(1, total_cases), 2)
        summary = {
            "model_type": model_type,
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": total_cases,
            "api_success_rate": round((api_success_count / total_cases) * 100, 2),
            "sql_validity_rate": round((valid_sql_count / total_cases) * 100, 2),
            "execution_success_rate": round((exec_success_count / total_cases) * 100, 2),
            "execution_accuracy": round((exec_accuracy_count / total_cases) * 100, 2),
            "avg_generation_time_ms": avg_latency,
            "gpu_status": self.qwen_engine.get_gpu_status() if model_type.startswith("qwen") else None,
            "detailed_results": detailed_results
        }

        # Save to outputs/evaluation
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.output_dir, f"eval_{model_type}_{timestamp_str}.json")
        csv_path = os.path.join(self.output_dir, f"eval_{model_type}_{timestamp_str}.csv")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Write CSV
        if detailed_results:
            keys = detailed_results[0].keys()
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(detailed_results)

        # Update latest evaluation summary cache
        latest_file = os.path.join(self.output_dir, "latest_evaluation_summary.json")
        existing_summaries = {}
        if os.path.exists(latest_file):
            try:
                with open(latest_file, "r", encoding="utf-8") as f:
                    existing_summaries = json.load(f)
            except Exception:
                existing_summaries = {}

        existing_summaries[model_type] = summary
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(existing_summaries, f, indent=2)

        summary["json_path"] = json_path
        summary["csv_path"] = csv_path
        return summary

