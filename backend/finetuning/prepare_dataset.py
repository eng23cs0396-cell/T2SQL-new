"""
Spider Dataset Preparation and Schema Formatting
Loads Spider dataset and tables schema metadata, formats instruction examples:
Input:
Database schema:
...
Question: ...
Output: ...
Saves train, validation, and test splits into data/processed/.
"""

import os
import json
import zipfile
import shutil
from typing import Dict, Any, List, Optional
from huggingface_hub import hf_hub_download
from datasets import load_dataset


class SpiderDatasetPreparer:
    """Prepares and caches Spider dataset and schema for few-shot and fine-tuning."""

    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed", db_dir: str = "data/databases"):
        self.raw_dir = os.path.abspath(raw_dir)
        self.processed_dir = os.path.abspath(processed_dir)
        self.db_dir = os.path.abspath(db_dir)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)

        self.tables_data: Dict[str, Dict[str, Any]] = {}
        self.schema_text_cache: Dict[str, str] = {}

    def extract_spider_assets(self) -> str:
        """Download and extract tables.json and starter sqlite databases from HAL-9001/spider-databases."""
        zip_path = hf_hub_download("HAL-9001/spider-databases", "spider_data.zip", repo_type="dataset")
        tables_target = os.path.join(self.raw_dir, "tables.json")

        with zipfile.ZipFile(zip_path, "r") as z:
            # Extract tables.json if not present
            if not os.path.exists(tables_target):
                with z.open("spider_data/tables.json") as src, open(tables_target, "wb") as dst:
                    shutil.copyfileobj(src, dst)

            # Extract selected representative Spider SQLite databases for evaluation & playground
            sample_dbs = [
                "department_management", "concert_singer", "course_teach",
                "car_1", "flight_2", "world_1", "student_transcripts_tracking"
            ]
            for db_id in sample_dbs:
                target_sqlite = os.path.join(self.db_dir, f"{db_id}.sqlite")
                if not os.path.exists(target_sqlite):
                    zip_member = f"spider_data/database/{db_id}/{db_id}.sqlite"
                    if zip_member in z.namelist():
                        with z.open(zip_member) as src, open(target_sqlite, "wb") as dst:
                            shutil.copyfileobj(src, dst)

        return tables_target

    def load_tables_schema(self) -> Dict[str, Dict[str, Any]]:
        """Parses tables.json into a structured schema lookup dictionary by db_id."""
        tables_file = os.path.join(self.raw_dir, "tables.json")
        if not os.path.exists(tables_file):
            self.extract_spider_assets()

        with open(tables_file, "r", encoding="utf-8") as f:
            raw_tables = json.load(f)

        db_map = {}
        for item in raw_tables:
            db_id = item["db_id"]
            table_names = item.get("table_names_original", item.get("table_names", []))
            col_names_raw = item.get("column_names_original", item.get("column_names", []))
            col_types = item.get("column_types", [])
            primary_keys = item.get("primary_keys", [])
            foreign_keys = item.get("foreign_keys", [])

            # Organize columns by table
            tables_dict = {t: [] for t in table_names}
            col_idx_to_info = {}

            for idx, (t_idx, col_name) in enumerate(col_names_raw):
                if t_idx == -1:
                    continue  # wildcard *
                t_name = table_names[t_idx]
                c_type = col_types[idx].upper() if idx < len(col_types) else "TEXT"
                is_pk = (idx in primary_keys)
                col_info = {"name": col_name, "type": c_type, "is_primary_key": is_pk}
                tables_dict[t_name].append(col_info)
                col_idx_to_info[idx] = (t_name, col_name)

            # Build relationships
            relationships = []
            for fk_from_idx, fk_to_idx in foreign_keys:
                if fk_from_idx in col_idx_to_info and fk_to_idx in col_idx_to_info:
                    from_t, from_c = col_idx_to_info[fk_from_idx]
                    to_t, to_c = col_idx_to_info[fk_to_idx]
                    relationships.append({
                        "from_table": from_t, "from_col": from_c,
                        "to_table": to_t, "to_col": to_c
                    })

            db_map[db_id] = {
                "tables": tables_dict,
                "relationships": relationships
            }

        self.tables_data = db_map
        return db_map

    def format_schema_text(self, db_id: str) -> str:
        """Returns standard readable schema text for prompt injection."""
        if db_id in self.schema_text_cache:
            return self.schema_text_cache[db_id]

        if not self.tables_data:
            self.load_tables_schema()

        if db_id not in self.tables_data:
            return f"Database schema for {db_id}:\n(Schema not found in catalog)"

        data = self.tables_data[db_id]
        lines = ["Database schema:\n"]
        for table_name, cols in data["tables"].items():
            lines.append(f"Table: {table_name}")
            for col in cols:
                pk_suffix = " PRIMARY KEY" if col["is_primary_key"] else ""
                lines.append(f"- {col['name']} {col['type']}{pk_suffix}")
            lines.append("")

        if data["relationships"]:
            lines.append("Relationships:")
            for rel in data["relationships"]:
                lines.append(f"- {rel['from_table']}.{rel['from_col']} references {rel['to_table']}.{rel['to_col']}")
            lines.append("")

        text = "\n".join(lines).strip()
        self.schema_text_cache[db_id] = text
        return text

    def prepare_and_save_splits(self, train_samples: int = 1500, val_samples: int = 300, test_samples: int = 200) -> Dict[str, str]:
        """
        Loads xlangai/spider dataset, constructs standard instruction format:
        {
           "id": int,
           "db_id": str,
           "instruction": "Database schema:\n...\n\nQuestion: ...",
           "output": "SELECT ...",
           "question": str,
           "query": str
        }
        Splits validation into independent validation and test sets to strictly prevent data leakage.
        """
        self.load_tables_schema()
        raw_ds = load_dataset("xlangai/spider")

        train_raw = raw_ds["train"]
        val_raw = raw_ds["validation"]

        # Format training split
        train_examples = []
        limit_train = min(train_samples, len(train_raw)) if train_samples > 0 else len(train_raw)
        for i in range(limit_train):
            item = train_raw[i]
            schema_txt = self.format_schema_text(item["db_id"])
            train_examples.append({
                "id": f"train_{i}",
                "db_id": item["db_id"],
                "instruction": f"{schema_txt}\n\nQuestion: {item['question']}",
                "output": item["query"],
                "question": item["question"],
                "query": item["query"],
                "schema_text": schema_txt
            })

        # Format validation split and separate held-out test split
        val_all = []
        for i in range(len(val_raw)):
            item = val_raw[i]
            schema_txt = self.format_schema_text(item["db_id"])
            val_all.append({
                "id": f"val_{i}",
                "db_id": item["db_id"],
                "instruction": f"{schema_txt}\n\nQuestion: {item['question']}",
                "output": item["query"],
                "question": item["question"],
                "query": item["query"],
                "schema_text": schema_txt
            })

        # Split val_all into validation and held-out test (no leakage)
        limit_val = min(val_samples, int(len(val_all) * 0.6))
        limit_test = min(test_samples, len(val_all) - limit_val)

        val_examples = val_all[:limit_val]
        test_examples = val_all[limit_val:limit_val + limit_test]

        train_path = os.path.join(self.processed_dir, "spider_train.json")
        val_path = os.path.join(self.processed_dir, "spider_val.json")
        test_path = os.path.join(self.processed_dir, "spider_test.json")

        with open(train_path, "w", encoding="utf-8") as f:
            json.dump(train_examples, f, indent=2)
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump(val_examples, f, indent=2)
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(test_examples, f, indent=2)

        return {
            "train_path": train_path,
            "val_path": val_path,
            "test_path": test_path,
            "train_count": len(train_examples),
            "val_count": len(val_examples),
            "test_count": len(test_examples)
        }


if __name__ == "__main__":
    preparer = SpiderDatasetPreparer()
    res = preparer.prepare_and_save_splits(train_samples=2000, val_samples=300, test_samples=200)
    print("Dataset preparation complete:", res)

