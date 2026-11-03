"""
SQL Validator and Safe Execution Engine
Uses SQLGlot for AST parsing and inspection, enforcing read-only constraints.
Executes queries safely via SQLite read-only URI mode and SQLite authorizer callbacks.
"""

import os
import re
import time
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import sqlglot
from sqlglot import exp


class SQLValidationError(Exception):
    """Raised when generated SQL fails security or syntax checks."""
    pass


class SQLExecutionError(Exception):
    """Raised when SQL execution fails."""
    pass


# Disallowed SQL statement types and operations
FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.Pragma,
)

# SQL authorizer actions to deny
# Deny table modifications, attachments, pragma, file access
DENIED_AUTHORIZER_ACTIONS = {
    sqlite3.SQLITE_INSERT,
    sqlite3.SQLITE_UPDATE,
    sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_TABLE,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_TABLE,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_PRAGMA,
}


def _sqlite_authorizer(action_code: int, param1: Optional[str], param2: Optional[str], db_name: Optional[str], trigger_or_view: Optional[str]) -> int:
    """SQLite runtime authorizer ensuring 100% read-only operations."""
    if action_code in DENIED_AUTHORIZER_ACTIONS:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


class SQLSecurityValidator:
    """Validates SQL query using SQLGlot parsing and schema verification."""

    @staticmethod
    def clean_sql_string(raw_sql: str) -> str:
        """Strip markdown code blocks, explanatory text, and trailing semicolons."""
        if not raw_sql:
            return ""

        # Remove markdown code blocks if present (```sql ... ```)
        text = raw_sql.strip()
        match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

        # Extract only the first SQL SELECT or WITH query if surrounded by conversational filler
        select_match = re.search(r"(?:SELECT|WITH)\s+[\s\S]+", text, re.IGNORECASE)
        if select_match:
            text = select_match.group(0).strip()

        # Remove multiple trailing semicolons
        text = text.rstrip(";")
        return text.strip()

    @classmethod
    def validate_sql(cls, raw_sql: str, allowed_tables: Optional[List[str]] = None) -> Tuple[str, exp.Expression]:
        """
        Validates that SQL:
        1. Is valid SQLite syntax.
        2. Contains exactly ONE statement.
        3. Is exclusively a SELECT or WITH statement.
        4. References valid tables if allowed_tables provided.
        Returns: (cleaned_sql, parsed_expression)
        """
        cleaned_sql = cls.clean_sql_string(raw_sql)
        if not cleaned_sql:
            raise SQLValidationError("Generated SQL query is empty.")

        # Check for multiple statements (semicolon split)
        try:
            statements = sqlglot.parse(cleaned_sql, read="sqlite")
        except Exception as e:
            raise SQLValidationError(f"SQL Syntax Error: {str(e)}")

        if not statements or len(statements) == 0:
            raise SQLValidationError("Failed to parse SQL query.")

        # Filter out None statements
        statements = [s for s in statements if s is not None]
        if len(statements) > 1:
            raise SQLValidationError("Multiple SQL statements detected. Only a single SELECT or WITH statement is allowed.")

        root_expr = statements[0]

        # Enforce that statement is a SELECT or WITH (which resolves to SELECT)
        if not isinstance(root_expr, (exp.Select, exp.Union)):
            # Check if root is WITH (CTE)
            if isinstance(root_expr, exp.Expression) and root_expr.key == "with":
                pass
            else:
                raise SQLValidationError(
                    f"Forbidden statement type: '{root_expr.key.upper()}'. Only read-only SELECT or WITH statements are allowed."
                )

        # Walk AST to ensure no nested forbidden expressions (e.g. INSERT into SELECT)
        for node in root_expr.walk():
            if isinstance(node, FORBIDDEN_EXPRESSIONS):
                raise SQLValidationError(f"Forbidden operation '{node.key.upper()}' detected inside query.")

        # Verify tables against database schema if provided
        if allowed_tables:
            allowed_set = {t.lower() for t in allowed_tables}
            referenced_tables = [table.name.lower() for table in root_expr.find_all(exp.Table) if table.name]
            for t in referenced_tables:
                if t not in allowed_set:
                    # Note: CTE names might be referenced, so check CTE names in query
                    ctes = {cte.alias.lower() for cte in root_expr.find_all(exp.CTE) if cte.alias}
                    if t not in allowed_set and t not in ctes:
                        raise SQLValidationError(f"Query references unknown table '{t}'. Allowed tables: {allowed_tables}")

        return cleaned_sql, root_expr


class SafeSQLExecutor:
    """Executes validated SQL queries against a SQLite database with strict timeouts and limits."""

    def __init__(self, db_path: str, timeout_seconds: float = 10.0, max_rows: int = 100):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")
        self.db_path = db_path
        self.timeout_seconds = timeout_seconds
        self.max_rows = max_rows

    def execute(self, sql_query: str, validate: bool = True, allowed_tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validates (optional) and executes read-only query.
        Returns:
            {
                "success": bool,
                "sql": str,
                "columns": List[str],
                "rows": List[List[Any]],
                "row_count": int,
                "execution_time_ms": float,
                "truncated": bool,
                "error": Optional[str]
            }
        """
        cleaned_sql = sql_query
        if validate:
            cleaned_sql, _ = SQLSecurityValidator.validate_sql(sql_query, allowed_tables=allowed_tables)

        # Connect with read-only URI and authorizer
        uri = f"file:{os.path.abspath(self.db_path)}?mode=ro"
        start_time = time.time()

        try:
            conn = sqlite3.connect(uri, uri=True, timeout=self.timeout_seconds)
            conn.set_authorizer(_sqlite_authorizer)
            cursor = conn.cursor()

            # Execute query
            cursor.execute(cleaned_sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch up to max_rows + 1 to detect truncation
            rows = cursor.fetchmany(self.max_rows + 1)
            truncated = len(rows) > self.max_rows
            if truncated:
                rows = rows[:self.max_rows]

            # Convert row tuples to list of lists (JSON serializable)
            serialized_rows = []
            for row in rows:
                serialized_rows.append([None if val is None else (float(val) if isinstance(val, float) else val) for val in row])

            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            conn.close()

            return {
                "success": True,
                "sql": cleaned_sql,
                "columns": columns,
                "rows": serialized_rows,
                "row_count": len(serialized_rows),
                "execution_time_ms": execution_time_ms,
                "truncated": truncated,
                "error": None
            }

        except Exception as e:
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "sql": cleaned_sql,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": execution_time_ms,
                "truncated": False,
                "error": str(e)
            }

