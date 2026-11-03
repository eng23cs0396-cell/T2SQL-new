"""
FastAPI Route Handlers for QueryMind Text-to-SQL Platform
Provides endpoints for database management, query generation, execution, comparison,
background fine-tuning, and evaluation metrics.
"""

import os
import json
import uuid
import threading
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.database.db_manager import DatabaseManager
from backend.database.schema_extractor import DatabaseSchemaExtractor
from backend.database.sql_validator import SafeSQLExecutor, SQLSecurityValidator
from backend.langchain_app.chains import TextToSQLPipeline
from backend.evaluation.compare_models import ModelComparisonService
from backend.evaluation.evaluate import ModelEvaluator
from backend.models.adapter_loader import AdapterManager
from backend.models.nemotron_api import NemotronSQLGenerator
from backend.models.qwen_model import LocalQwenEngine
from backend.finetuning.train_lora import LoRATrainer
from backend.finetuning.training_config import LoRATrainingConfig

router = APIRouter(prefix="/api")

# Singleton Services
db_manager = DatabaseManager()
pipeline = TextToSQLPipeline()
comparison_svc = ModelComparisonService()
evaluator = ModelEvaluator()
adapter_manager = AdapterManager()
nemotron_gen = NemotronSQLGenerator()
qwen_engine = LocalQwenEngine.get_instance()

# In-memory background jobs registry
BACKGROUND_JOBS: Dict[str, Dict[str, Any]] = {}


# ============================================================
# PYDANTIC REQUEST & RESPONSE SCHEMAS
# ============================================================

class GenerateRequest(BaseModel):
    database_id: str
    question: str
    model: str = Field(default="nemotron", description="'nemotron' or 'qwen'")
    technique: str = Field(default="zero_shot", description="'zero_shot', 'few_shot', or 'lora'")
    num_few_shot_examples: int = Field(default=3, ge=1, le=5)
    adapter_name: Optional[str] = None


class ExecuteRequest(BaseModel):
    database_id: str
    sql: str


class CompareRequest(BaseModel):
    database_id: str
    question: str
    num_few_shot_examples: int = Field(default=3, ge=1, le=5)
    adapter_name: Optional[str] = None


class EvaluationRunRequest(BaseModel):
    model_type: str = Field(default="nemotron", description="'nemotron', 'qwen_few_shot', 'qwen_lora'")
    test_limit: int = Field(default=10, ge=1, le=50)
    adapter_name: Optional[str] = None


class StartFineTuningRequest(BaseModel):
    adapter_name: str = "qwen_lora_spider"
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    max_steps: int = 50
    batch_size: int = 1
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 512


# ============================================================
# 1. SYSTEM & HEALTH
# ============================================================

@router.get("/health")
def get_health():
    """System health check and GPU diagnostics."""
    gpu = qwen_engine.get_gpu_status()
    has_nemotron = nemotron_gen.is_configured()
    return {
        "status": "online",
        "gpu": gpu,
        "nemotron_configured": has_nemotron,
        "database_count": len(db_manager.list_databases()),
        "adapter_count": len(adapter_manager.list_adapters())
    }


@router.get("/models")
def get_available_models():
    """Information on supported models, techniques, and loaded adapters."""
    adapters = adapter_manager.list_adapters()
    gpu = qwen_engine.get_gpu_status()
    return {
        "models": [
            {
                "id": "nemotron",
                "name": "NVIDIA Nemotron 3.5 Lightning",
                "full_id": "nvidia/nemotron-3.5-lightning-30b-a3b",
                "type": "Cloud API (NVIDIA NIM)",
                "techniques": [
                    {"id": "zero_shot", "name": "Direct Zero-Shot (Thinking Disabled)", "default": True}
                ],
                "ready": nemotron_gen.is_configured(),
                "description": "30B parameter model optimized for high-throughput reasoning and instant SQL synthesis."
            },
            {
                "id": "qwen",
                "name": "Local Qwen2.5-Coder-3B-Instruct",
                "full_id": "Qwen/Qwen2.5-Coder-3B-Instruct",
                "type": "Local GPU (NVIDIA RTX 4060 8GB)",
                "techniques": [
                    {"id": "few_shot", "name": "Few-Shot Prompting (Spider Exemplars)", "default": True},
                    {"id": "lora", "name": "LoRA Fine-Tuned Adapter", "default": False}
                ],
                "ready": True,
                "description": "3B parameter coding model running locally with 16-bit precision and PEFT LoRA adapters."
            }
        ],
        "adapters": adapters,
        "gpu_status": gpu
    }


# ============================================================
# 2. DATABASE MANAGEMENT
# ============================================================

@router.get("/database/list")
def list_databases():
    """List all available SQLite databases."""
    return db_manager.list_databases()


@router.post("/database/upload")
async def upload_database(file: UploadFile = File(...)):
    """Upload a SQLite database file (.db, .sqlite, .sqlite3)."""
    try:
        contents = await file.read()
        res = db_manager.save_uploaded_file(file.filename, contents)
        return {"success": True, "database": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/database/{database_id}/schema")
def get_database_schema(database_id: str):
    """Dynamically extracts tables, columns, primary keys, and foreign keys."""
    try:
        path = db_manager.get_database_path(database_id)
        extractor = DatabaseSchemaExtractor(path)
        return extractor.extract_full_schema()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/database/{database_id}/tables")
def get_database_tables(database_id: str):
    """Lists table names for a database."""
    try:
        path = db_manager.get_database_path(database_id)
        extractor = DatabaseSchemaExtractor(path)
        return {"database_id": database_id, "tables": extractor.get_tables()}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/database/{database_id}/preview/{table_name}")
def get_table_preview(database_id: str, table_name: str, limit: int = 10):
    """Preview records from a table."""
    try:
        path = db_manager.get_database_path(database_id)
        extractor = DatabaseSchemaExtractor(path)
        return extractor.get_table_preview(table_name, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# 3. TEXT-TO-SQL GENERATION & EXECUTION
# ============================================================

@router.post("/generate")
def generate_sql(req: GenerateRequest):
    """
    LangChain orchestrated Text-to-SQL generation.
    Retrieves dynamic schema, constructs prompt, invokes selected model,
    validates SQL with SQLGlot, and executes safe read-only query.
    """
    try:
        res = pipeline.run(
            database_id=req.database_id,
            question=req.question,
            model=req.model,
            technique=req.technique,
            num_few_shot_examples=req.num_few_shot_examples,
            adapter_name=req.adapter_name
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
def execute_sql(req: ExecuteRequest):
    """Safely execute a user-edited or generated SQL query against the database."""
    try:
        path = db_manager.get_database_path(req.database_id)
        extractor = DatabaseSchemaExtractor(path)
        allowed_tables = extractor.get_tables()

        executor = SafeSQLExecutor(path)
        res = executor.execute(req.sql, validate=True, allowed_tables=allowed_tables)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare")
def compare_models(req: CompareRequest):
    """Compare Nemotron, Qwen Few-Shot, and Qwen LoRA side-by-side on the same schema & question."""
    try:
        res = comparison_svc.compare(
            database_id=req.database_id,
            question=req.question,
            num_few_shot_examples=req.num_few_shot_examples,
            adapter_name=req.adapter_name
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 4. FINE-TUNING LAB
# ============================================================

@router.get("/finetuning/adapters")
def list_adapters():
    """List all trained LoRA adapters."""
    return adapter_manager.list_adapters()


@router.post("/finetuning/preflight")
def finetuning_preflight(config: Optional[LoRATrainingConfig] = None):
    """Inspect GPU, available VRAM, and verify readiness for LoRA fine-tuning."""
    trainer = LoRATrainer(config)
    return trainer.preflight_check()


@router.post("/finetuning/start")
def start_finetuning(req: StartFineTuningRequest, background_tasks: BackgroundTasks):
    """Launches a non-blocking background LoRA fine-tuning worker."""
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    # Validate GPU preflight first
    config = LoRATrainingConfig(
        adapter_name=req.adapter_name,
        lora_rank=req.lora_rank,
        lora_alpha=req.lora_alpha,
        lora_dropout=req.lora_dropout,
        max_steps=req.max_steps,
        batch_size=req.batch_size,
        gradient_accumulation_steps=req.gradient_accumulation_steps,
        learning_rate=req.learning_rate,
        max_seq_length=req.max_seq_length
    )

    trainer = LoRATrainer(config)
    preflight = trainer.preflight_check()
    if not preflight["can_train"]:
        raise HTTPException(status_code=400, detail="; ".join(preflight["issues"]))

    job_state = {
        "job_id": job_id,
        "type": "LORA_FINETUNING",
        "status": "QUEUED",
        "current_step": 0,
        "total_steps": req.max_steps,
        "progress_percentage": 0.0,
        "loss_history": [],
        "val_loss_history": [],
        "current_train_loss": None,
        "current_val_loss": None,
        "elapsed_time_seconds": 0.0,
        "eta_seconds": None,
        "error": None,
        "config": config.model_dump()
    }
    BACKGROUND_JOBS[job_id] = job_state

    def worker():
        trainer.run_training(job_state)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return {"job_id": job_id, "status": "QUEUED", "message": "Fine-tuning job started in background."}


@router.get("/finetuning/status/{job_id}")
def get_finetuning_status(job_id: str):
    """Poll progress, current step, loss curves, and ETA of fine-tuning job."""
    if job_id not in BACKGROUND_JOBS:
        raise HTTPException(status_code=404, detail="Fine-tuning job not found.")
    return BACKGROUND_JOBS[job_id]


# ============================================================
# 5. EVALUATION DASHBOARD
# ============================================================

@router.post("/evaluation/run")
def run_evaluation(req: EvaluationRunRequest):
    """
    Launches evaluation of a model against held-out Spider test cases in a background thread.
    """
    job_id = f"eval_{uuid.uuid4().hex[:8]}"
    job_state = {
        "job_id": job_id,
        "type": "EVALUATION",
        "model_type": req.model_type,
        "status": "RUNNING",
        "test_limit": req.test_limit,
        "result": None,
        "error": None
    }
    BACKGROUND_JOBS[job_id] = job_state

    def worker():
        try:
            res = evaluator.evaluate_model(
                model_type=req.model_type,
                test_limit=req.test_limit,
                adapter_name=req.adapter_name
            )
            job_state["status"] = "COMPLETED"
            job_state["result"] = res
        except Exception as e:
            job_state["status"] = "FAILED"
            job_state["error"] = str(e)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return {"job_id": job_id, "status": "RUNNING", "message": f"Evaluation for '{req.model_type}' initiated."}


@router.get("/evaluation/status/{job_id}")
def get_evaluation_status(job_id: str):
    """Check status of background evaluation job."""
    if job_id not in BACKGROUND_JOBS:
        raise HTTPException(status_code=404, detail="Evaluation job not found.")
    return BACKGROUND_JOBS[job_id]


@router.get("/evaluation/results")
def get_latest_evaluation_results():
    """Retrieve the latest real evaluation results summary for charting."""
    summary_file = os.path.join(evaluator.output_dir, "latest_evaluation_summary.json")
    if os.path.exists(summary_file):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


@router.get("/evaluation/export")
def export_evaluation(format: str = Query("json"), model_type: Optional[str] = None):
    """Export evaluation results file for download."""
    # Find latest eval file
    files = [f for f in os.listdir(evaluator.output_dir) if f.startswith("eval_") and f.endswith(f".{format}")]
    if model_type:
        files = [f for f in files if f"_{model_type}_" in f]

    if not files:
        raise HTTPException(status_code=404, detail=f"No {format.upper()} evaluation export available yet.")

    latest_file = sorted(files)[-1]
    file_path = os.path.join(evaluator.output_dir, latest_file)
    media_type = "text/csv" if format == "csv" else "application/json"
    return FileResponse(file_path, media_type=media_type, filename=latest_file)
