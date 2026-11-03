"""
Evaluation Test Case Loader
Loads held-out test cases from Spider test split with matching local SQLite instances.
"""

import os
import json
from typing import List, Dict, Any, Optional


class TestCaseLoader:
    """Loads held-out evaluation test cases with ground-truth SQL and schemas."""

    def __init__(self, test_path: str = "data/processed/spider_test.json", db_dir: str = "data/databases"):
        self.test_path = os.path.abspath(test_path)
        self.db_dir = os.path.abspath(db_dir)

    def get_test_cases(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads and returns test cases where the local database instance exists."""
        if not os.path.exists(self.test_path):
            raise FileNotFoundError(f"Test cases file not found at {self.test_path}. Run dataset prep first.")

        with open(self.test_path, "r", encoding="utf-8") as f:
            all_cases = json.load(f)

        valid_cases = []
        for case in all_cases:
            db_id = case["db_id"]
            # Look for db_id.sqlite or db_id.db in data/databases
            db_candidates = [
                os.path.join(self.db_dir, f"{db_id}.sqlite"),
                os.path.join(self.db_dir, f"{db_id}.db")
            ]
            found_path = next((p for p in db_candidates if os.path.exists(p)), None)
            if found_path:
                valid_cases.append({
                    "id": case["id"],
                    "db_id": db_id,
                    "db_path": found_path,
                    "database_id": os.path.basename(found_path),
                    "question": case["question"],
                    "gold_sql": case["query"],
                    "schema_text": case.get("schema_text", "")
                })

        if limit:
            return valid_cases[:limit]
        return valid_cases

