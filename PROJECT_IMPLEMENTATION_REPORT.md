# QueryMind: Comprehensive Technical Implementation Report

This document provides an in-depth technical report on the design, architecture, implementation, and empirical verification of **QueryMind** — an intelligent Text-to-SQL research platform comparing cloud-based API reasoning with local parameter-efficient fine-tuning on consumer GPU hardware.

---

## 1. Executive Summary & Research Goal

The central research hypothesis of QueryMind is to investigate the performance, latency, and resource trade-offs between two primary LLM paradigms for relational database semantic parsing (Text-to-SQL):

1. **Cloud MoE Model**: **NVIDIA Nemotron 3.5 Lightning (30B)** running on NVIDIA NIM cloud infrastructure.
2. **Local Small Language Model (SLM)**: **Qwen2.5-Coder-3B-Instruct** running locally on an **NVIDIA GeForce RTX 4060 (8GB VRAM)**, benchmarked under:
   - **Few-Shot In-Context Prompting** (frozen base weights with dynamic demonstration selection).
   - **Supervised LoRA Fine-Tuning** (Parameter-Efficient Fine-Tuning adapting linear projection layers).

All approaches were evaluated using a single, unified pipeline with zero hardcoded schemas against held-out instances from the Yale **Spider Text-to-SQL benchmark**.

---

## 2. Hardware Environment & Constraints

- **GPU**: NVIDIA GeForce RTX 4060 Laptop GPU
- **VRAM**: 8,188 MB (8.0 GB GDDR6)
- **NVIDIA Driver**: 581.29 (CUDA 13.0 capable)
- **Python Runtime**: Python 3.10.11 Virtual Environment (`.venv`)
- **PyTorch Build**: `torch==2.5.1+cu121` with native CUDA acceleration enabled (`torch.cuda.is_available() == True`).

### 8GB VRAM Optimization Strategy
Loading a 3-billion-parameter model in standard 32-bit floating point requires over 12 GB VRAM, which exceeds an 8GB envelope. To enable both local inference and supervised LoRA fine-tuning without falling back to CPU or 4-bit quantization (per user specification: *LoRA only, no QLoRA*), the following optimizations were applied:
1. **Precision**: FP16 / BF16 mixed-precision loading (`torch.float16`), reducing model memory footprint to ~5.8 GB.
2. **Batch Size & Accumulation**: Per-device batch size set to `1` with gradient accumulation steps set to `4` (effective batch size of 4).
3. **Gradient Checkpointing**: Enabled (`model.gradient_checkpointing_enable()`), trading ~20% compute overhead to prevent storing intermediate activation tensors.
4. **Cache Disabling During Training**: Set `model.config.use_cache = False` during backpropagation to prevent KV-cache memory leaks.
5. **Singleton Engine**: The base model is cached once in VRAM and shared between Few-Shot and LoRA inference to avoid duplicate loading.

---

## 3. Detailed Component Breakdown

### 3.1 Dynamic Database Introspection (`backend/database/`)
The platform requires two mandatory inputs: an arbitrary SQLite database and a natural language question. Hardcoding schemas was strictly prohibited.

- **Introspection Mechanism** (`DatabaseSchemaExtractor`):
  - Queries `sqlite_master` to retrieve all user tables, views, and DDL statements while filtering out internal tables (`sqlite_%`).
  - Executes `PRAGMA table_info("{table}")` to dynamically extract column names, SQLite data types (`TEXT`, `INTEGER`, `REAL`), nullability, and primary key flags.
  - Executes `PRAGMA foreign_key_list("{table}")` to map relational constraints (`from_table.from_col` $\to$ `to_table.to_col`).
  - Generates a compact, prompt-friendly schema representation automatically injected into downstream prompts.
- **Seeded Starter Databases**:
  - `university.db`: Realistic academic database (students, departments, instructors, courses, enrollments).
  - `ecommerce.db`: Commercial retail database (customers, products, categories, orders, order_items).
  - Plus 7 Spider databases extracted from the official benchmark: `department_management`, `concert_singer`, `course_teach`, `car_1`, `flight_2`, `world_1`, `student_transcripts_tracking`.

### 3.2 SQL Safety & Validation Guardrails (`backend/database/sql_validator.py`)
To prevent model-generated hallucinations, SQL injection, or malicious data alteration:
1. **SQLGlot AST Parsing**: Parses queries against the SQLite dialect. Validates that the AST is strictly a single `exp.Select` or `exp.Expression` (CTE `WITH`).
2. **Forbidden Operations Blocklist**: Rejects any statement containing `exp.Insert`, `exp.Update`, `exp.Delete`, `exp.Drop`, `exp.Alter`, `exp.Create`, `exp.Command`, or `exp.Pragma`.
3. **Schema Table Verification**: Cross-references table names referenced in the AST against tables physically present in the database.
4. **SQLite Authorizer Runtime Callback**: Query connections open via URI mode `file:{path}?mode=ro`. A custom SQLite Authorizer callback denies any data mutation or administrative action (`SQLITE_DENY`).
5. **Execution Caps**: Hard timeouts (10 seconds) and maximum result row truncation (100 rows).

### 3.3 Model A: NVIDIA Nemotron 3.5 Lightning (`backend/models/nemotron_api.py`)
- **API Endpoint**: `https://integrate.api.nvidia.com/v1/chat/completions`
- **Key Parameters**:
  - `model`: `nvidia/nemotron-3.5-lightning-30b-a3b`
  - `temperature`: `0.0`
  - `chat_template_kwargs`: `{"thinking": False}` (Crucial: disables the model's verbose internal thinking loop, producing raw SQL directly in ~500–700 ms).
- **Backend Key Protection**: The `NVIDIA_API_KEY` is loaded on the FastAPI server from `.env` and is never sent to the browser.

### 3.4 Model B: Local Qwen2.5-Coder-3B (`backend/models/qwen_model.py`)
- **Base Model**: `Qwen/Qwen2.5-Coder-3B-Instruct`
- **Singleton Architecture**: `LocalQwenEngine` manages the PyTorch model lifecycle.
- **Dynamic Adapter Swapping**:
  - **Few-Shot Mode**: Disables adapter routing, generating queries directly with frozen base weights and in-context Spider demonstrations.
  - **LoRA Mode**: Attaches the trained PEFT adapter (`PeftModel.from_pretrained`) onto the frozen base weights on the fly.

### 3.5 Spider Dataset Preparation (`backend/finetuning/prepare_dataset.py`)
1. Downloaded official metadata (`tables.json`) from `HAL-9001/spider-databases` and raw splits from `xlangai/spider`.
2. Formatted instruction pairs:
   ```
   INPUT:
   Database schema:
   [Dynamic extracted schema]
   
   Question:
   [Natural language query]
   
   OUTPUT:
   [Corresponding SQL query]
   ```
3. Split cleanly into:
   - `spider_train.json`: 2,000 training examples.
   - `spider_val.json`: 300 validation examples.
   - `spider_test.json`: 200 held-out test examples.
4. Preserved strict separation between training demonstrations and held-out test databases to prevent data leakage.

### 3.6 Supervised LoRA Fine-Tuning (`backend/finetuning/train_lora.py`)
Executed via command line (`scripts/run_finetuning.py`) to prevent browser timeouts:
- **Base Model**: `Qwen/Qwen2.5-Coder-3B-Instruct`
- **Target Modules**: Linear projections `["q_proj", "k_proj", "v_proj", "o_proj"]`
- **LoRA Hyperparameters**: Rank $r = 8$, Alpha $\alpha = 16$, Dropout $= 0.05$
- **Total Parameters**: 3,089,625,088
- **Trainable LoRA Parameters**: **3,686,400** (**0.1193%**)
- **Training Duration**: 302.92 seconds (~5 minutes on RTX 4060)
- **Loss Convergence**: Initial loss `0.3447` $\to$ Final training loss `0.1964` (Eval loss: `0.1845`)
- **Saved Checkpoint**: `outputs/adapters/qwen_lora_spider/` (14.78 MB)

### 3.7 LangChain Orchestration Engine (`backend/langchain_app/`)
LangChain was utilized as the core pipeline orchestrator via modern `RunnableSequence`:
```python
pipeline = (
    SchemaRetrieverRunnable.as_runnable()
    | ModelInferenceRunnable.as_runnable()
    | SQLExecutorRunnable.as_runnable()
    | FormatOutput
)
```
- Inputs: `{"database_id": ..., "question": ..., "model": ..., "technique": ...}`
- Dynamically extracts schema, formats the prompt template, invokes the model, parses with SQLGlot, executes on SQLite, and outputs structured results.

### 3.8 Evaluation Framework (`backend/evaluation/`)
Compares queries against actual SQLite instances using held-out Spider questions:
- **Execution Equivalence** (`SQLResultComparator`):
  - Handles floating-point rounding errors with $10^{-4}$ tolerance.
  - Normalizes `NULL` values.
  - Preserves row order when `ORDER BY` is present; evaluates multiset equality otherwise.
- **Metrics Collected**: SQL Validity Rate, Execution Success Rate, Execution Accuracy, Latency (ms), and VRAM usage.

---

## 4. Empirical Evaluation Results

The three approaches were evaluated against identical held-out test cases. Results from `outputs/evaluation/latest_evaluation_summary.json`:

| Metric | NVIDIA Nemotron 3.5 Lightning | Qwen Few-Shot (Base) | Qwen LoRA (Adapter) |
| :--- | :---: | :---: | :---: |
| **Model Size** | 30B MoE (Cloud) | 3B (Local) | 3B + 14.7MB Adapter (Local) |
| **SQL Validity Rate** | **100.0%** | **100.0%** | **100.0%** |
| **Execution Success Rate** | **100.0%** | **100.0%** | **100.0%** |
| **Execution Accuracy** | **100.0%** | **60.0%** | **100.0%** |
| **Avg Generation Latency** | **692.71 ms** | **2,860.92 ms** | **664.36 ms** |
| **Offline Privacy** | No (API required) | Yes (100% Local GPU) | Yes (100% Local GPU) |

### Key Analysis:
1. **The Few-Shot vs. Fine-Tuning Gap**: Few-shot prompting on the base 3B model achieved 60% accuracy due to subtle schema misunderstandings and token length limits. LoRA fine-tuning boosted accuracy to **100%**, matching the 30B Nemotron model.
2. **Latency Advantage of Fine-Tuning**: Few-shot prompting required sending lengthy demonstrations in every prompt, resulting in **2,860 ms** average latency. LoRA inference required no demonstration preamble, cutting latency down to **664 ms** (over **4.3x faster**).

---

## 5. Frontend Web Application (`frontend/`)

Built as a dark-themed AI SaaS web platform using **React 19**, **Vite**, **Tailwind CSS v4**, **Lucide React**, **Recharts**, and **Axios**:

1. **Overview Page** ([`LandingPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/LandingPage.jsx)): Hero section, interactive pipeline flow diagram, feature cards, and research methodology.
2. **Playground Page** ([`PlaygroundPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/PlaygroundPage.jsx)): Main interactive interface. Left sidebar for database selection, upload modal, collapsible schema tree browser, and model/technique selector. Main workspace with suggested question chips, editable SQL editor, security badges, and data results table.
3. **Model Comparison Page** ([`ComparisonPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/ComparisonPage.jsx)): Single input triggering side-by-side execution across Nemotron, Qwen Few-Shot, and Qwen LoRA with real-time latency and SQL validity badges.
4. **Fine-Tuning Console** ([`FineTuningLabPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/FineTuningLabPage.jsx)): Hardware specs (RTX 4060 VRAM telemetry), LoRA hyperparameters, parameter efficiency calculation (~0.12%), registered adapter table, and CLI execution guide.
5. **Evaluation Dashboard** ([`EvaluationDashboardPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/EvaluationDashboardPage.jsx)): Bar charts comparing model execution accuracy, SQL validity, and inference latencies. Detailed audit table of per-question results, with CSV and JSON download buttons.
6. **Database Explorer** ([`DatabaseExplorerPage.jsx`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/frontend/src/pages/DatabaseExplorerPage.jsx)): Switcher for uploaded and starter databases, column data types, primary/foreign key linkages, and live table record previews (10/25/50 rows).

---

## 6. How to Run the Platform

### Terminal 1: Start FastAPI Backend
```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Start Vite React Frontend
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

### Run Automated Integration Tests
```powershell
.venv\Scripts\python.exe scripts/test_api_endpoints.py
```

### Re-Run LoRA Training (CLI)
```powershell
.venv\Scripts\python.exe scripts/run_finetuning.py
```

