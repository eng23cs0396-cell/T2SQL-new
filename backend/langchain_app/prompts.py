"""
LangChain Prompt Templates for Text-to-SQL
Provides structured ChatPromptTemplates for Nemotron, Few-shot Qwen, and LoRA Qwen.
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
from backend.prompting.few_shot import FewShotPromptManager


# System instructions for strict SQL generation
BASE_SYSTEM_INSTRUCTION = (
    "You are an expert SQL engineer. Given a database schema and a user question, "
    "generate ONLY an executable SQLite query that accurately answers the question.\n"
    "Follow these rules strictly:\n"
    "1. Output ONLY the raw SQL query. No explanations, no thoughts, no markdown fences.\n"
    "2. Generate only read-only SELECT or WITH statements.\n"
    "3. Use exact table and column names matching the schema.\n"
    "4. Join tables correctly using foreign keys."
)

# Standard zero-shot template (used by Nemotron or direct instruction)
NEMOTRON_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(BASE_SYSTEM_INSTRUCTION),
    HumanMessagePromptTemplate.from_template(
        "{schema_text}\n\nQuestion: {question}\n\nSQL Query:"
    )
])

# Few-shot template generator that incorporates dynamic Spider exemplars
class LangChainFewShotPromptFactory:
    """Constructs LangChain prompts with relevant few-shot exemplars."""

    def __init__(self):
        self.few_shot_mgr = FewShotPromptManager()

    def create_prompt(self, schema_text: str, question: str, num_examples: int = 3) -> str:
        return self.few_shot_mgr.build_prompt(
            schema_text=schema_text,
            question=question,
            num_examples=num_examples
        )

