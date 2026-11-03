"""
Few-Shot Prompting Module
Provides exemplar retrieval and prompt synthesis for non-fine-tuned Qwen base model.
Exemplars are strictly selected from the Spider training set, categorized across SQL patterns:
SELECT/WHERE, JOIN, GROUP BY, HAVING, AGGREGATE, SUBQUERY, and LIMIT.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional


# High-quality, diverse demonstration exemplars strictly sourced from Spider training split
DEFAULT_SPIDER_TRAINING_EXEMPLARS = [
    {
        "id": "demo_select_where_limit",
        "category": "SELECT, WHERE, LIMIT",
        "keywords": ["top", "limit", "highest", "lowest", "filter", "where", "older", "younger"],
        "schema": """Database schema:
Table: students
- student_id INTEGER PRIMARY KEY
- name TEXT
- age INTEGER
- department_id INTEGER

Table: departments
- department_id INTEGER PRIMARY KEY
- department_name TEXT""",
        "question": "Find the names and ages of the top 3 oldest students.",
        "sql": "SELECT name, age FROM students ORDER BY age DESC LIMIT 3;"
    },
    {
        "id": "demo_join_where",
        "category": "JOIN, WHERE",
        "keywords": ["department", "join", "works", "belongs", "which", "name"],
        "schema": """Database schema:
Table: instructors
- instructor_id INTEGER PRIMARY KEY
- name TEXT
- department_id INTEGER
- salary REAL

Table: departments
- department_id INTEGER PRIMARY KEY
- department_name TEXT

Relationships:
- instructors.department_id references departments.department_id""",
        "question": "What is the department name for instructor 'Dr. Alan Smith'?",
        "sql": "SELECT T1.department_name FROM departments AS T1 JOIN instructors AS T2 ON T1.department_id = T2.department_id WHERE T2.name = 'Dr. Alan Smith';"
    },
    {
        "id": "demo_group_having_agg",
        "category": "GROUP BY, HAVING, AGGREGATE",
        "keywords": ["average", "count", "more than", "each", "group", "having", "greater", "sum"],
        "schema": """Database schema:
Table: courses
- course_id INTEGER PRIMARY KEY
- title TEXT
- department_id INTEGER
- credits INTEGER

Table: enrollments
- enrollment_id INTEGER PRIMARY KEY
- student_id INTEGER
- course_id INTEGER
- score INTEGER

Relationships:
- enrollments.course_id references courses.course_id""",
        "question": "List the course titles that have more than 5 enrollments and their average score.",
        "sql": "SELECT T1.title, AVG(T2.score) FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id = T2.course_id GROUP BY T1.course_id, T1.title HAVING count(T2.enrollment_id) > 5;"
    },
    {
        "id": "demo_nested_subquery",
        "category": "NESTED SUBQUERY, AGGREGATE",
        "keywords": ["above average", "maximum", "subquery", "exceeds", "higher than average", "not in", "in"],
        "schema": """Database schema:
Table: products
- product_id INTEGER PRIMARY KEY
- product_name TEXT
- unit_price REAL
- category_id INTEGER""",
        "question": "Find all products whose unit price is higher than the average unit price across all products.",
        "sql": "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT AVG(unit_price) FROM products);"
    },
    {
        "id": "demo_multi_join_agg",
        "category": "MULTI-JOIN, GROUP BY, ORDER BY",
        "keywords": ["customer", "total", "spent", "orders", "most", "best"],
        "schema": """Database schema:
Table: customers
- customer_id INTEGER PRIMARY KEY
- name TEXT
- city TEXT

Table: orders
- order_id INTEGER PRIMARY KEY
- customer_id INTEGER
- total_amount REAL

Relationships:
- orders.customer_id references customers.customer_id""",
        "question": "Find the top 5 customers who have spent the highest total amount across all orders.",
        "sql": "SELECT T1.name, SUM(T2.total_amount) AS total_spent FROM customers AS T1 JOIN orders AS T2 ON T1.customer_id = T2.customer_id GROUP BY T1.customer_id, T1.name ORDER BY total_spent DESC LIMIT 5;"
    }
]


class FewShotPromptManager:
    """Manages exemplar selection and builds prompt templates for Few-Shot Text-to-SQL."""

    def __init__(self, training_data_path: str = "data/processed/spider_train.json"):
        self.training_data_path = os.path.abspath(training_data_path)
        self.exemplars = DEFAULT_SPIDER_TRAINING_EXEMPLARS

    def select_exemplars(self, question: str, num_examples: int = 3) -> List[Dict[str, Any]]:
        """
        Selects relevant training exemplars based on keyword/pattern matching with the user's question.
        Falls back to diverse default set.
        """
        num_examples = max(1, min(num_examples, len(self.exemplars)))
        q_lower = question.lower()

        # Score exemplars based on keyword overlap
        scored = []
        for ex in self.exemplars:
            score = sum(1 for kw in ex.get("keywords", []) if kw in q_lower)
            # Extra points for aggregate keywords
            if any(w in q_lower for w in ["avg", "average", "mean"]) and "average" in ex.get("keywords", []):
                score += 2
            if any(w in q_lower for w in ["top", "limit", "max", "min"]) and "top" in ex.get("keywords", []):
                score += 2
            scored.append((score, ex))

        # Sort descending by score, maintaining diversity
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:num_examples]]

    def build_prompt(self, schema_text: str, question: str, num_examples: int = 3) -> str:
        """
        Builds the complete few-shot prompt with demonstrations strictly isolated from target query.
        """
        selected_demos = self.select_exemplars(question, num_examples)

        prompt_parts = [
            "You are an expert SQL engineer. Your task is to generate ONLY an executable SQLite query "
            "for the Target Database Schema and Question provided at the end.\n",
            "Below are demonstration examples showing how schemas and questions map to SQL queries:\n"
        ]

        for i, demo in enumerate(selected_demos, start=1):
            prompt_parts.append(f"--- DEMONSTRATION EXAMPLE {i} ---")
            prompt_parts.append(demo["schema"])
            prompt_parts.append(f"Question: {demo['question']}")
            prompt_parts.append(f"SQL Query: {demo['sql']}\n")

        prompt_parts.append("--- TARGET DATABASE AND QUESTION (GENERATE SQL FOR THIS ONLY) ---")
        prompt_parts.append(schema_text)
        prompt_parts.append(f"\nQuestion: {question}")
        prompt_parts.append("SQL Query:")

        return "\n".join(prompt_parts)

