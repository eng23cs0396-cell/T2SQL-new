"""
LangChain SQL Validation & Execution Runnable
Enforces AST security parsing and executes read-only queries with timeouts and limits.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableLambda
from backend.database.sql_validator import SafeSQLExecutor, SQLSecurityValidator, SQLValidationError


class SQLExecutorRunnable:
    """Runnable that validates and executes generated SQL query."""

    def __init__(self, timeout_seconds: float = 10.0, max_rows: int = 100):
        self.timeout_seconds = timeout_seconds
        self.max_rows = max_rows

    def execute_step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input dictionary must contain 'sql' (or 'generated_sql') and 'db_path'.
        Optionally contains 'allowed_tables'.
        """
        raw_sql = inputs.get("sql") or inputs.get("generated_sql", "")
        db_path = inputs.get("db_path")
        allowed_tables = inputs.get("tables")

        # Step 1: SQL AST validation
        try:
            cleaned_sql, parsed_ast = SQLSecurityValidator.validate_sql(
                raw_sql,
                allowed_tables=allowed_tables
            )
            validation_status = {"valid": True, "error": None}
        except SQLValidationError as ve:
            return {
                **inputs,
                "cleaned_sql": SQLSecurityValidator.clean_sql_string(raw_sql),
                "validation": {"valid": False, "error": str(ve)},
                "execution": {
                    "success": False,
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": 0.0,
                    "error": f"Validation Error: {str(ve)}"
                }
            }

        # Step 2: Safe read-only execution
        executor = SafeSQLExecutor(
            db_path=db_path,
            timeout_seconds=self.timeout_seconds,
            max_rows=self.max_rows
        )

        exec_res = executor.execute(cleaned_sql, validate=False)

        return {
            **inputs,
            "cleaned_sql": cleaned_sql,
            "validation": validation_status,
            "execution": exec_res
        }

    def as_runnable(self):
        return RunnableLambda(self.execute_step)

