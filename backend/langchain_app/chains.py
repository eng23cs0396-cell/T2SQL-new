"""
LangChain Orchestration Chains
Builds complete Runnable sequences for:
Database + User Question -> Schema Extraction -> Prompt Construction -> Model -> SQL Validation -> Safe Execution -> Results.
"""

from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableLambda, RunnableSequence

from backend.langchain_app.schema_retriever import SchemaRetrieverRunnable
from backend.langchain_app.sql_executor import SQLExecutorRunnable
from backend.models.nemotron_api import NemotronSQLGenerator
from backend.models.qwen_model import LocalQwenEngine


class ModelInferenceRunnable:
    """Invokes selected model (Nemotron, Qwen Few-shot, Qwen LoRA) in a LangChain chain."""

    def __init__(self):
        self.nemotron_client = NemotronSQLGenerator()
        self.qwen_engine = LocalQwenEngine.get_instance()

    def generate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        model_name = inputs.get("model", "nemotron")
        technique = inputs.get("technique", "zero_shot")  # 'few_shot' or 'lora' or 'zero_shot'
        schema_text = inputs.get("schema_text", "")
        question = inputs.get("question", "")
        num_few_shot = inputs.get("num_few_shot_examples", 3)
        adapter_name = inputs.get("adapter_name")

        if model_name == "nemotron":
            res = self.nemotron_client.generate_sql(schema_text, question)
            return {
                **inputs,
                "sql": res.get("sql", ""),
                "raw_response": res.get("raw_response", ""),
                "generation_time_ms": res.get("latency_ms", 0.0),
                "token_usage": res.get("token_usage", {}),
                "model_used": "nvidia/nemotron-3.5-lightning-30b-a3b",
                "technique_used": "NVIDIA NIM API",
                "model_error": res.get("error")
            }
        else:
            # Local Qwen
            mode = "lora" if technique == "lora" else "few_shot"
            res = self.qwen_engine.generate_sql(
                schema_text=schema_text,
                question=question,
                mode=mode,
                num_few_shot_examples=num_few_shot,
                adapter_name=adapter_name
            )
            return {
                **inputs,
                "sql": res.get("sql", ""),
                "raw_response": res.get("raw_response", ""),
                "generation_time_ms": res.get("latency_ms", 0.0),
                "model_used": "Qwen/Qwen2.5-Coder-3B-Instruct",
                "technique_used": f"Local Qwen ({mode.replace('_', ' ').title()})",
                "output_tokens": res.get("output_tokens", 0),
                "gpu_status": res.get("gpu_status", {}),
                "model_error": res.get("error")
            }

    def as_runnable(self):
        return RunnableLambda(self.generate)


def format_final_output(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Formats final response dictionary for the frontend API."""
    return {
        "success": inputs.get("execution", {}).get("success", False) and not bool(inputs.get("model_error")),
        "question": inputs.get("question"),
        "database_id": inputs.get("database_id"),
        "model_used": inputs.get("model_used"),
        "technique_used": inputs.get("technique_used"),
        "generated_sql": inputs.get("cleaned_sql") or inputs.get("sql", ""),
        "raw_response": inputs.get("raw_response", ""),
        "generation_time_ms": inputs.get("generation_time_ms", 0.0),
        "validation": inputs.get("validation", {"valid": False, "error": "Not validated"}),
        "execution": inputs.get("execution", {}),
        "gpu_status": inputs.get("gpu_status"),
        "error": inputs.get("model_error") or inputs.get("execution", {}).get("error")
    }


class TextToSQLPipeline:
    """Constructs and runs orchestrated LangChain Text-to-SQL pipelines."""

    def __init__(self):
        self.schema_retriever = SchemaRetrieverRunnable()
        self.model_invoker = ModelInferenceRunnable()
        self.sql_executor = SQLExecutorRunnable()
        self.formatter = RunnableLambda(format_final_output)

        # Full LangChain Runnable Sequence
        self.pipeline: RunnableSequence = (
            self.schema_retriever.as_runnable()
            | self.model_invoker.as_runnable()
            | self.sql_executor.as_runnable()
            | self.formatter
        )

    def run(
        self,
        database_id: str,
        question: str,
        model: str = "nemotron",
        technique: str = "zero_shot",
        num_few_shot_examples: int = 3,
        adapter_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes full Text-to-SQL pipeline using LangChain."""
        inputs = {
            "database_id": database_id,
            "question": question,
            "model": model,
            "technique": technique,
            "num_few_shot_examples": num_few_shot_examples,
            "adapter_name": adapter_name
        }
        return self.pipeline.invoke(inputs)

