"""
Comprehensive Benchmark Script for Multi-Table Databases
Evaluates Local Qwen (Few-Shot and LoRA) across 24 complex queries on 7 databases.
Computes:
- SQL Validity Rate (AST validation via SQLGlot)
- Execution Success Rate (Safe read-only execution)
- Strict Execution Accuracy (Exact positional match)
- Semantic Execution Accuracy (Permutation-invariant column match)
- Latency per query
"""

import os
import sys
import json
import time
import sqlite3

sys.path.insert(0, os.path.abspath("."))

from backend.database.schema_extractor import DatabaseSchemaExtractor
from backend.database.sql_validator import SafeSQLExecutor, SQLSecurityValidator, SQLValidationError
from backend.models.qwen_model import LocalQwenEngine
from backend.evaluation.metrics import SQLResultComparator
from backend.evaluation.test_cases import TestCaseLoader


def check_permutation_equal(pred_rows, gold_rows, order_sensitive=False):
    """Checks if any column permutation of pred_rows matches gold_rows."""
    if not pred_rows and not gold_rows:
        return True
    if len(pred_rows) != len(gold_rows):
        return False
    if not pred_rows or not gold_rows:
        return False
    
    num_cols = len(gold_rows[0])
    if len(pred_rows[0]) != num_cols:
        return False

    import itertools
    for p in itertools.permutations(range(num_cols)):
        permuted_pred = [[row[i] for i in p] for row in pred_rows]
        if SQLResultComparator.compare_results(permuted_pred, gold_rows, order_sensitive=order_sensitive):
            return True
    return False


def run_benchmark(model_mode="lora", limit=24):
    loader = TestCaseLoader()
    cases = loader.get_test_cases(limit=limit)
    print(f"Loaded {len(cases)} test cases.")

    engine = LocalQwenEngine.get_instance()
    results = []

    valid_count = 0
    exec_success_count = 0
    strict_acc_count = 0
    semantic_acc_count = 0
    latencies = []

    for i, c in enumerate(cases, 1):
        db_id = c["db_id"]
        db_path = c["db_path"]
        question = c["question"]
        gold_sql = c["gold_sql"]

        extractor = DatabaseSchemaExtractor(db_path)
        schema_data = extractor.extract_full_schema()
        schema_text = schema_data["formatted_text"]
        allowed_tables = list(schema_data["tables"].keys())
        executor = SafeSQLExecutor(db_path=db_path)

        # Gold execution
        gold_res = executor.execute(gold_sql, validate=False)
        gold_rows = gold_res.get("rows", [])

        # Model generation
        t0 = time.time()
        gen = engine.generate_sql(schema_text, question, mode=model_mode, num_few_shot_examples=3)
        gen_time = (time.time() - t0) * 1000
        latencies.append(gen_time)
        pred_raw = gen.get("sql", "")

        # Validation
        cleaned_sql = pred_raw
        is_valid = False
        val_err = None
        try:
            cleaned_sql, _ = SQLSecurityValidator.validate_sql(pred_raw, allowed_tables=allowed_tables)
            is_valid = True
            valid_count += 1
        except Exception as e:
            val_err = str(e)

        # Execution
        is_exec_ok = False
        is_strict_acc = False
        is_semantic_acc = False
        pred_rows = []
        exec_err = None

        if is_valid:
            ex = executor.execute(cleaned_sql, validate=False)
            if ex.get("success"):
                is_exec_ok = True
                exec_success_count += 1
                pred_rows = ex.get("rows", [])
                order_sens = "order by" in gold_sql.lower()
                is_strict_acc = SQLResultComparator.compare_results(pred_rows, gold_rows, order_sensitive=order_sens)
                is_semantic_acc = check_permutation_equal(pred_rows, gold_rows, order_sensitive=order_sens)
                if is_strict_acc:
                    strict_acc_count += 1
                if is_semantic_acc:
                    semantic_acc_count += 1
            else:
                exec_err = ex.get("error")

        results.append({
            "case_id": c["id"],
            "db_id": db_id,
            "question": question,
            "gold_sql": gold_sql,
            "predicted_sql": cleaned_sql,
            "valid_sql": is_valid,
            "execution_success": is_exec_ok,
            "strict_accuracy": is_strict_acc,
            "semantic_accuracy": is_semantic_acc,
            "latency_ms": round(gen_time, 2),
            "error": val_err or exec_err
        })

        status_str = "ACC" if is_semantic_acc else ("EXEC_OK" if is_exec_ok else "ERR")
        print(f"[{i:2d}/{len(cases)}] {db_id:<22} | {status_str:<7} | {round(gen_time):4d}ms | Q: {question[:50]}...")

    n = len(cases)
    summary = {
        "model_mode": model_mode,
        "total_cases": n,
        "sql_validity_rate": round(valid_count / n * 100, 2),
        "execution_success_rate": round(exec_success_count / n * 100, 2),
        "strict_accuracy": round(strict_acc_count / n * 100, 2),
        "semantic_accuracy": round(semantic_acc_count / n * 100, 2),
        "avg_latency_ms": round(sum(latencies) / n, 2),
        "detailed_results": results
    }
    return summary


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "lora"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    print(f"=== Running Multi-Table Benchmark (Mode: {mode}, Limit: {limit}) ===")
    summ = run_benchmark(model_mode=mode, limit=limit)
    print("\n=== SUMMARY ===")
    print(f"Total Cases:            {summ['total_cases']}")
    print(f"SQL Validity Rate:      {summ['sql_validity_rate']}%")
    print(f"Execution Success Rate: {summ['execution_success_rate']}%")
    print(f"Strict Accuracy:        {summ['strict_accuracy']}%")
    print(f"Semantic Accuracy:      {summ['semantic_accuracy']}%")
    print(f"Avg Latency:            {summ['avg_latency_ms']} ms")
