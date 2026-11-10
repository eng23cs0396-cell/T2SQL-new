import time
import sys
import os

sys.path.insert(0, os.path.abspath("."))

def step(msg):
    global t
    print(f"[{round(time.time() - t, 3)}s] {msg}", flush=True)
    t = time.time()

t = time.time()
step("Starting test")

from backend.database.db_manager import DatabaseManager
step("Imported db_manager")

db_mgr = DatabaseManager()
step("Instantiated db_manager")

from backend.langchain_app.chains import TextToSQLPipeline
step("Imported TextToSQLPipeline")

pipeline = TextToSQLPipeline()
step("Instantiated TextToSQLPipeline")

from backend.evaluation.compare_models import ModelComparisonService
step("Imported ModelComparisonService")

comparison_svc = ModelComparisonService()
step("Instantiated ModelComparisonService")

from backend.evaluation.evaluate import ModelEvaluator
step("Imported ModelEvaluator")

evaluator = ModelEvaluator()
step("Instantiated ModelEvaluator")

from backend.models.adapter_loader import AdapterManager
step("Imported AdapterManager")

adapter_manager = AdapterManager()
step("Instantiated AdapterManager")

from backend.models.nemotron_api import NemotronSQLGenerator
step("Imported NemotronSQLGenerator")

nemotron_gen = NemotronSQLGenerator()
step("Instantiated NemotronSQLGenerator")

from backend.models.qwen_model import LocalQwenEngine
step("Imported LocalQwenEngine")

qwen_engine = LocalQwenEngine.get_instance()
step("Instantiated LocalQwenEngine")

from backend.finetuning.train_lora import LoRATrainer
step("Imported LoRATrainer")

from backend.finetuning.training_config import LoRATrainingConfig
step("Imported LoRATrainingConfig")

from backend.api.routes import router
step("Imported routes.router")
print("ALL ROUTE IMPORTS COMPLETED SUCCESSFULLY!", flush=True)
