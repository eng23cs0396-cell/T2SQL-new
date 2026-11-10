import sys
import os

sys.path.insert(0, os.path.abspath("."))
from backend.evaluation.evaluate import ModelEvaluator

evaluator = ModelEvaluator()
summary = evaluator.evaluate_model("qwen_lora", test_limit=20)
print("\nEvaluation completed on 20 multi-table cases!")
print(f"SQL Validity Rate:   {summary['sql_validity_rate']}%")
print(f"Execution Success:   {summary['execution_success_rate']}%")
print(f"Execution Accuracy:  {summary['execution_accuracy']}%")
print(f"Average Latency ms:  {summary['avg_generation_time_ms']} ms")
print("-" * 75)
for res in summary["detailed_results"]:
    print(f"{res['db_id']:<22} | Acc: {str(res['execution_accuracy']):<5} | Valid: {str(res['valid_sql']):<5} | {res['question'][:40]}")
