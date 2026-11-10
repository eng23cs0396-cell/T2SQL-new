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
    def _compare_rows_unordered(cls, predicted_rows: List[List[Any]], gold_rows: List[List[Any]]) -> bool:
        """Unordered comparison: check multiset row equivalence."""
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

    @classmethod
    def _compare_single_alignment(cls, predicted_rows: List[List[Any]], gold_rows: List[List[Any]], order_sensitive: bool = False) -> bool:
        if order_sensitive:
            return all(cls.are_rows_equal(r1, r2) for r1, r2 in zip(predicted_rows, gold_rows))
        return cls._compare_rows_unordered(predicted_rows, gold_rows)

    @classmethod
    def compare_results(cls, predicted_rows: List[List[Any]], gold_rows: List[List[Any]], order_sensitive: bool = False) -> bool:
        """
        Compares predicted query result set against gold ground truth.
        Supports order sensitivity, NULL/float tolerances, and column projection permutation tolerance.
        """
        if len(predicted_rows) != len(gold_rows):
            return False

        if len(predicted_rows) == 0:
            return True

        # 1. Direct comparison
        if cls._compare_single_alignment(predicted_rows, gold_rows, order_sensitive=order_sensitive):
            return True

        # 2. Check if a column permutation satisfies semantic equivalence
        if len(predicted_rows[0]) == len(gold_rows[0]):
            num_cols = len(gold_rows[0])
            if 1 < num_cols <= 5:
                import itertools
                for perm in itertools.permutations(range(num_cols)):
                    permuted = [[row[i] for i in perm] for row in predicted_rows]
                    if cls._compare_single_alignment(permuted, gold_rows, order_sensitive=order_sensitive):
                        return True

        return False

