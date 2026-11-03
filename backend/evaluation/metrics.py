"""
SQL Execution Accuracy and Metric Evaluator
Compares result sets of predicted SQL vs gold/ground-truth SQL queries on SQLite.
Handles floating-point tolerance, NULL value equivalence, and order sensitivity.
"""

import math
from typing import List, Any, Tuple, Optional


class SQLResultComparator:
    """Evaluates semantic execution equivalence between two SQL query results."""

    FLOAT_TOLERANCE = 1e-4

    @classmethod
    def are_values_equal(cls, val1: Any, val2: Any) -> bool:
        """Compares two individual cell values with NULL and float tolerances."""
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False

        # Numeric comparison
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return math.isclose(float(val1), float(val2), rel_tol=cls.FLOAT_TOLERANCE, abs_tol=cls.FLOAT_TOLERANCE)

        # String normalization (whitespace strip and case-insensitive check if needed)
        str1 = str(val1).strip().lower()
        str2 = str(val2).strip().lower()

        # Try float conversion on strings
        try:
            f1 = float(str1)
            f2 = float(str2)
            return math.isclose(f1, f2, rel_tol=cls.FLOAT_TOLERANCE, abs_tol=cls.FLOAT_TOLERANCE)
        except ValueError:
            pass

        return str1 == str2

    @classmethod
    def are_rows_equal(cls, row1: List[Any], row2: List[Any]) -> bool:
        """Compares two rows."""
        if len(row1) != len(row2):
            return False
        return all(cls.are_values_equal(v1, v2) for v1, v2 in zip(row1, row2))

    @classmethod
    def compare_results(cls, predicted_rows: List[List[Any]], gold_rows: List[List[Any]], order_sensitive: bool = False) -> bool:
        """
        Compares predicted query result set against gold ground truth.
        order_sensitive: True if ORDER BY is present and row order is strict.
        """
        if len(predicted_rows) != len(gold_rows):
            return False

        if len(predicted_rows) == 0:
            return True

        if order_sensitive:
            return all(cls.are_rows_equal(r1, r2) for r1, r2 in zip(predicted_rows, gold_rows))

        # Unordered comparison: check multiset equivalence
        matched_indices = set()
        for p_row in predicted_rows:
            found = False
            for g_idx, g_row in enumerate(gold_rows):
                if g_idx not in matched_indices and cls.are_rows_equal(p_row, g_row):
                    matched_indices.add(g_idx)
                    found = True
                    break
            if not found:
                return False

        return len(matched_indices) == len(gold_rows)

