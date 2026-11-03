"""
Database Schema Extractor
Dynamically extracts tables, columns, primary keys, foreign keys, and relationships
from SQLite databases using PRAGMA and sqlite_master.
"""

import sqlite3
from typing import Dict, List, Any, Optional
import os


class DatabaseSchemaExtractor:
    """Extracts rich schema representation from SQLite database."""

    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        # Open in read-only URI mode to prevent any modification during schema extraction
        uri = f"file:{os.path.abspath(self.db_path)}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def get_tables(self) -> List[str]:
        """Fetch list of user tables (excluding sqlite internal tables)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
            )
            return [row["name"] for row in cursor.fetchall()]

    def extract_full_schema(self) -> Dict[str, Any]:
        """
        Extract complete schema dictionary:
        - tables: map of table_name -> {columns, primary_keys, foreign_keys, row_count}
        - relationships: list of {from_table, from_col, to_table, to_col}
        - ddl: create table statements from sqlite_master
        - formatted_text: readable text prompt representation
        """
        tables_data = {}
        relationships = []
        ddl_statements = []

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Retrieve all user tables and views
            cursor.execute(
                "SELECT name, sql FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name;"
            )
            table_rows = cursor.fetchall()

            for t_row in table_rows:
                table_name = t_row["name"]
                sql_ddl = t_row["sql"]
                if sql_ddl:
                    ddl_statements.append(sql_ddl.strip() + ";")

                # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                cursor.execute(f'PRAGMA table_info("{table_name}");')
                cols_info = cursor.fetchall()

                columns = []
                pks = []
                for col in cols_info:
                    is_pk = bool(col["pk"])
                    col_dict = {
                        "name": col["name"],
                        "type": col["type"] or "TEXT",
                        "notnull": bool(col["notnull"]),
                        "default_value": col["dflt_value"],
                        "is_primary_key": is_pk
                    }
                    columns.append(col_dict)
                    if is_pk:
                        pks.append(col["name"])

                # PRAGMA foreign_key_list returns: id, seq, table, from, to, on_update, on_delete, match
                cursor.execute(f'PRAGMA foreign_key_list("{table_name}");')
                fks_info = cursor.fetchall()
                foreign_keys = []
                for fk in fks_info:
                    fk_dict = {
                        "from_col": fk["from"],
                        "to_table": fk["table"],
                        "to_col": fk["to"]
                    }
                    foreign_keys.append(fk_dict)
                    relationships.append({
                        "from_table": table_name,
                        "from_col": fk["from"],
                        "to_table": fk["table"],
                        "to_col": fk["to"]
                    })

                # Row count estimate (safe read-only)
                try:
                    cursor.execute(f'SELECT COUNT(*) as cnt FROM "{table_name}";')
                    row_count = cursor.fetchone()["cnt"]
                except Exception:
                    row_count = 0

                tables_data[table_name] = {
                    "columns": columns,
                    "primary_keys": pks,
                    "foreign_keys": foreign_keys,
                    "row_count": row_count
                }

        formatted_text = self._build_formatted_schema_text(tables_data, relationships)

        return {
            "tables": tables_data,
            "relationships": relationships,
            "ddl": "\n\n".join(ddl_statements),
            "formatted_text": formatted_text
        }

    def _build_formatted_schema_text(self, tables_data: Dict[str, Any], relationships: List[Dict[str, str]]) -> str:
        """
        Builds the readable schema representation required for LLM prompt ingestion:
        Example:
        Table: students
        - student_id INTEGER PRIMARY KEY
        - name TEXT
        - age INTEGER
        - department_id INTEGER

        Relationship:
        - students.department_id references departments.department_id
        """
        lines = ["Database schema:\n"]
        for table_name, data in tables_data.items():
            lines.append(f"Table: {table_name}")
            for col in data["columns"]:
                pk_suffix = " PRIMARY KEY" if col["is_primary_key"] else ""
                lines.append(f"- {col['name']} {col['type']}{pk_suffix}")
            lines.append("")

        if relationships:
            lines.append("Relationships:")
            for rel in relationships:
                lines.append(f"- {rel['from_table']}.{rel['from_col']} references {rel['to_table']}.{rel['to_col']}")
            lines.append("")

        return "\n".join(lines).strip()

    def get_table_preview(self, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch sample records from a specific table."""
        # Sanitize table name against known tables to avoid injection
        tables = self.get_tables()
        if table_name not in tables:
            raise ValueError(f"Table '{table_name}' does not exist in database.")

        limit = max(1, min(limit, 50))  # Max 50 rows preview

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'PRAGMA table_info("{table_name}");')
            columns = [c["name"] for c in cursor.fetchall()]

            cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit};')
            rows = cursor.fetchall()
            row_dicts = [dict(row) for row in rows]

            return {
                "table_name": table_name,
                "columns": columns,
                "rows": row_dicts,
                "total_rows_previewed": len(row_dicts)
            }

