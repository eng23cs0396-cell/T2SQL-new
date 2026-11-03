# QueryMind – Intelligent Text-to-SQL LLM Platform

QueryMind is a professional academic and research-oriented Text-to-SQL platform built from scratch. Its primary objective is to demonstrate, compare, and benchmark two distinct LLM paradigms for converting natural language questions into accurate, executable SQL queries:

1. **High-Throughput Cloud API Reasoning**: NVIDIA Nemotron 3.5 Lightning (30B parameter MoE architecture via NVIDIA NIM API).
2. **Local Privacy-Preserving GPU Inference**: Qwen2.5-Coder-3B-Instruct running on local NVIDIA hardware (RTX 4060 with 8GB VRAM) evaluated under both **Few-Shot Prompting** and **Supervised LoRA Fine-Tuning**.

---

## Architecture Overview

```
                                      Mandatory User Inputs
                        ┌────────────────────────┴────────────────────────┐
                        │                                                 │
            Target SQLite Database                              User Question
                        │                                                 │
                        ▼                                                 ▼
            [Dynamic Schema Extractor]                               [NLP Query]
            - PRAGMA table_info                                           │
            - PRAGMA foreign_key_list                                     │
            - sqlite_master                                               │
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                [LangChain Orchestration Engine]
                                - SchemaRetrieverRunnable
                                - ModelInferenceRunnable
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        │                                                 │
                        ▼                                                 ▼
            [NVIDIA Nemotron 3.5 API]                          [Local Qwen2.5-Coder-3B]
            - nvidia/nemotron-3.5-lightning-30b-a3b            - Hugging Face Transformers
            - Thinking Disabled for instant SQL                - 16-bit CUDA on RTX 4060
            - Temperature = 0.0                                - In-Context Few-Shot (Spider)
            - Latency: ~500–700 ms                             - PEFT LoRA Adapter (Rank 8)
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                      [SQLGlot AST Validator]
                                      - Validates SQLite syntax
                                      - Rejects mutations / multi-statement attacks
                                                 │
                                                 ▼
                                  [Safe Read-Only SQLite Executor]
                                  - URI mode=ro with SQLite Authorizer
                                  - Query timeouts & row caps
                                                 │
                                                 ▼
                                    [Vite + React 19 Frontend]
                                    - 6 SaaS Pages with Dark Theme
```

---

## Empirical Benchmark Findings

The three approaches were benchmarked on held-out Spider test instances against actual SQLite databases. Metrics are stored in `outputs/evaluation/latest_evaluation_summary.json`:

| Model / Technique | SQL Validity Rate | Execution Accuracy | Avg Generation Latency | Execution Environment |
| :--- | :---: | :---: | :---: | :--- |
| **NVIDIA Nemotron 3.5 Lightning** | **100.0%** | **100.0%** | **692.71 ms** | Cloud NIM API (`temperature: 0.0`) |
| **Qwen Few-Shot (Base Model)** | **100.0%** | **60.0%** | **2,860.92 ms** | Local GPU (RTX 4060), 3 Spider Exemplars |
| **Qwen LoRA (Trained Adapter)** | **100.0%** | **100.0%** | **664.36 ms** | Local GPU (RTX 4060), Rank-8 Adapter |

> **Key Research Takeaways**:
> 1. **Accuracy Jump**: LoRA fine-tuning boosted execution accuracy on held-out instances from **60% to 100%**, demonstrating that parameter-efficient domain adaptation significantly reduces hallucinations and syntax misalignment.
> 2. **Inference Latency Reduction**: Qwen LoRA inference ran in **664 ms** compared to **2,860 ms** for Few-Shot prompting (~4.3x speedup) because the prompt contains only the immediate schema and question without lengthy demonstration exemplars.
> 3. **Competitive Parity**: The 3B local LoRA model matches the execution accuracy of the 30B cloud API model while running completely offline within an 8GB VRAM envelope.

---

## Two-Model Architecture

### Model A: NVIDIA Nemotron 3.5 Lightning
- **Model ID**: `nvidia/nemotron-3.5-lightning-30b-a3b`
- **Endpoint**: `https://integrate.api.nvidia.com/v1/chat/completions`
- **Configuration**: `temperature: 0.0`, `max_tokens: 512`, `chat_template_kwargs: {"thinking": False}` to disable internal reasoning latency and output direct SQL.
- **Security**: The `NVIDIA_API_KEY` is loaded strictly on the backend and is never exposed to frontend code or client bundles.

### Model B: Local Qwen2.5-Coder-3B-Instruct
- **Model ID**: `Qwen/Qwen2.5-Coder-3B-Instruct`
- **Hardware Optimization**: Runs on NVIDIA GeForce RTX 4060 (8GB VRAM) in FP16 precision. Uses lazy loading and singleton model management to ensure base weights are loaded only once in memory.
- **Two Modalities**:
  1. **Few-Shot In-Context Prompting**: Dynamic exemplar selection from Spider training demonstrations without modifying model weights.
  2. **LoRA Fine-Tuned Adapter**: Parameter-efficient adaptation loaded dynamically via PEFT (`PeftModel.from_pretrained`), swapping adapter modules on top of frozen base weights.

---

## Dynamic Schema Extraction

QueryMind strictly enforces that schemas are never hardcoded:
- Accepts `.db`, `.sqlite`, and `.sqlite3` files uploaded through the web UI or pre-loaded in `data/databases/`.
- Dynamic introspection using SQLite metadata:
  - `sqlite_master` for active user tables and views.
  - `PRAGMA table_info("{table_name}")` for column names, data types, and primary keys.
  - `PRAGMA foreign_key_list("{table_name}")` for relational foreign key links between tables.
- Builds readable, prompt-optimized schema representations automatically.

---

## Few-Shot Prompting (Spider Training Set)

- Sourced strictly from the **Spider training split** to prevent data contamination with validation and test benchmarks.
- Demonstrations cover diverse SQL patterns:
  - `SELECT`, `WHERE`, `LIMIT`
  - `INNER JOIN` and multi-table relationships
  - `GROUP BY`, `HAVING`, and aggregate functions (`COUNT`, `AVG`, `SUM`, `MAX`)
  - Nested subqueries (`WHERE col > (SELECT AVG(...))`)
- Dynamic keyword and intent matching selects the most semantically relevant 3 to 5 demonstrations for each incoming question.

---

## LoRA Fine-Tuning (8GB VRAM RTX 4060)

Fine-tuning is tailored for the 8GB VRAM constraint of the RTX 4060:
- **Framework**: Hugging Face PEFT + Transformers.
- **Base Checkpoint**: `Qwen/Qwen2.5-Coder-3B-Instruct` (frozen base weights).
- **LoRA Parameters**:
  - Rank ($r$): 8
  - Alpha ($\alpha$): 16
  - Dropout: 0.05
  - Target Modules: `["q_proj", "k_proj", "v_proj", "o_proj"]`
- **Memory Optimizations**:
  - Batch size: 1
  - Gradient accumulation steps: 4
  - Gradient checkpointing: enabled with `model.config.use_cache = False`
  - Precision: FP16 mixed precision
  - Optimizer: `adamw_torch`
- **Trained Adapter**: Saved in `outputs/adapters/qwen_lora_spider` (14.78 MB).
- **Trainable Parameters**: **3,686,400** parameters (**0.1193%** of 3.09B total parameters).
- **Execution**: Managed via CLI (`python scripts/run_finetuning.py`) to prevent browser timeouts and provide complete GPU telemetry. The Fine-Tuning Lab in the UI provides architectural inspection, hyperparameter review, and adapter registry status.

---

## Common Evaluation Framework

- Benchmarks all three approaches on identical held-out test cases from the **Spider test split** against real SQLite instances (`data/databases/`).
- **Metrics Measured**:
  - API / Generation Success Rate (%)
  - SQL Validity Rate (%) parsed via SQLGlot
  - Execution Success Rate (%)
  - Execution Accuracy (% semantic multiset match against gold SQL query results)
  - Average Generation Latency (ms)
- **Methodology**:
  - Floating point comparison with $10^{-4}$ tolerance.
  - NULL equivalence handling.
  - Order-sensitivity enforcement when `ORDER BY` is present; multiset equality otherwise.
- Export results as JSON and CSV for independent verification.

---

## SQL Safety & Execution Guardrails

- **AST Validation**: Every model output is parsed with SQLGlot. Statements must be strictly single `SELECT` or `WITH` queries. Any `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `ATTACH`, `DETACH`, or `PRAGMA` is immediately rejected.
- **Read-Only SQLite Engine**: Opened using URI `mode=ro` with custom SQLite Authorizer callbacks (`sqlite3.SQLITE_DENY` on modifying opcodes).
- **Resource Limits**: 10-second execution timeouts and 100-row result caps.

---

## Getting Started

### Prerequisites
- Windows 10/11 with NVIDIA GPU (RTX 4060 with 8GB VRAM recommended).
- Python 3.10 or 3.11.
- Node.js (v18+) and npm.
- NVIDIA NIM API Key (obtain from [build.nvidia.com](https://build.nvidia.com)).

### 1. Environment Setup

Create `.env` in the project root:
```ini
NVIDIA_API_KEY=nvapi-your-key-here
HOST=127.0.0.1
PORT=8000
```

### 2. Backend Setup
Using `uv` or standard Python virtual environment:
```powershell
# Create virtual environment
uv venv .venv --python 3.10

# Activate virtual environment
.venv\Scripts\activate

# Install PyTorch with CUDA 12.1
uv pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio

# Install backend dependencies
uv pip install -r backend/requirements.txt
```

### 3. Spider Dataset Preparation
Download tables schema and format training/validation/test splits:
```powershell
.venv\Scripts\python.exe backend/finetuning/prepare_dataset.py
```

### 4. Running LoRA Fine-Tuning (Optional / Pre-Trained)
To train or re-train the Qwen LoRA adapter on your RTX 4060 GPU:
```powershell
.venv\Scripts\python.exe scripts/run_finetuning.py
```

### 5. Run Backend Server
```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation is live at: `http://127.0.0.1:8000/docs`

### 6. Frontend Setup
In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```
Web application is accessible at: `http://localhost:5173`

---

## Running Integration Tests

To run the automated end-to-end integration test suite:
```powershell
.venv\Scripts\python.exe scripts/test_api_endpoints.py
```

---

## Web Pages Included

1. **Overview (Landing Page)**: Hero section, architectural diagram, feature highlights, and research methodology.
2. **Playground**: Main interactive interface with dynamic database selector, schema tree viewer, model/technique selector, suggestion chips, SQL editor, and data table preview.
3. **Model Comparison**: Side-by-side execution of Nemotron, Qwen Few-Shot, and Qwen LoRA on any selected database and question.
4. **Fine-Tuning Lab**: Dedicated architectural specification console, hyperparameter review, parameter efficiency calculator, and adapter registry.
5. **Evaluation Dashboard**: Real empirical metrics, accuracy/validity comparison bar charts, latency plots, detailed per-case results table, and CSV/JSON export buttons.
6. **Database Explorer**: Database switcher, table schema inspector, foreign key relationships browser, and live table data preview with row limits.

---

## Additional Documentation

For a detailed technical walkthrough of all components, hardware configurations, and implementation methodologies, see [`PROJECT_IMPLEMENTATION_REPORT.md`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/PROJECT_IMPLEMENTATION_REPORT.md).
