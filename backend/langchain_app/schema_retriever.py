"""
LangChain Schema Retriever Runnable
Wraps DatabaseSchemaExtractor as a LangChain Runnable for dynamic schema pipeline integration.
"""

from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableLambda
from backend.database.schema_extractor import DatabaseSchemaExtractor
from backend.database.db_manager import DatabaseManager


class SchemaRetrieverRunnable:
    """Retrieves and formats database schema dynamically in a LangChain pipeline."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()

    def retrieve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input dictionary must contain 'database_id' (or 'db_path') and 'question'.
        Outputs enhanced dictionary containing 'schema_text', 'tables', and 'relationships'.
        """
        database_id = inputs.get("database_id")
        db_path = inputs.get("db_path")

        if not db_path and database_id:
            db_path = self.db_manager.get_database_path(database_id)

        if not db_path:
            raise ValueError("Neither 'database_id' nor 'db_path' provided in pipeline inputs.")

        extractor = DatabaseSchemaExtractor(db_path)
        schema_data = extractor.extract_full_schema()

        return {
            **inputs,
            "db_path": db_path,
            "schema_text": schema_data["formatted_text"],
            "tables": list(schema_data["tables"].keys()),
            "schema_details": schema_data
        }

    def as_runnable(self):
        """Convert to LangChain RunnableLambda."""
        return RunnableLambda(self.retrieve)

