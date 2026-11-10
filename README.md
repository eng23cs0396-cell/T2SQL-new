# QueryMind – Text-to-SQL LLM Platform

QueryMind turns natural-language questions and SQLite databases into safe, read-only SQL queries, executes them in real time, and renders the result data tables. It compares two generation paths:

1. **High-Throughput Cloud API**: **NVIDIA Nemotron 3.5 Lightning** (`nvidia/nemotron-3.5-lightning-30b-a3b`) through the NVIDIA NIM API.
2. **Local Privacy-Preserving GPU Inference**: **Qwen2.5-Coder-3B-Instruct** running on local NVIDIA hardware (RTX 4060 with 8GB VRAM) evaluated under both **Spider Few-Shot Prompting** and **Supervised LoRA Fine-Tuning**.

Schemas are dynamically extracted from SQLite databases at request time. Generated SQL is validated using SQLGlot AST parsing and executed through a strict read-only SQLite connection.

---

## Architecture

```
            SQLite Database                         Natural Question
                    │                                      │
                    ▼                                      │
         Dynamic Schema Extractor                          │
         (sqlite_master, PRAGMA table_info,               │
          PRAGMA foreign_key_list)                         │
                    │                                      │
                    └──────────────┬───────────────────────┘
                                   ▼
                    Nemotron API   or    Local Qwen
                    (NVIDIA NIM)         (Few-Shot / LoRA)
                                   │
                                   ▼
                         SQLGlot AST Validator
                     (Single SELECT / WITH only)
                                   │
                                   ▼
                    Read-Only SQLite Executor
                  (mode=ro, Authorizer, Row Cap)
                                   │
                                   ▼
                         Vite + React Frontend
```

---

## Evaluation & Benchmark Results

The platform includes an automated benchmark evaluating model performance across databases scaling from 3 to 12 tables (`veterinary_clinic`, `film_production`, `research_grants`, `maritime_shipping`):

| Model Architecture | Deployment | SQL Validity | Execution Success | Right Answers (Accuracy) | Avg Latency |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **NVIDIA Nemotron 3.5 Lightning** | Cloud API (NIM) | **100.0%** | **95.0%** | **85.0%** (17/20) | **1,173.95 ms** |
| **Qwen2.5-Coder-3B (Few-Shot)** | Local RTX 4060 GPU | **100.0%** | **90.0%** | **85.0%** (17/20) | **3,132.06 ms** |
| **Qwen2.5-Coder-3B (LoRA Adapter)** | Local RTX 4060 GPU | **100.0%** | **90.0%** | **85.0%** (17/20) | **3,690.99 ms** |

Detailed empirical metrics, error breakdowns, and per-query comparisons are documented in [RESULTS.md](RESULTS.md).

---

## Quick Start Guide (Clone & Run on Any Laptop)

Follow these step-by-step instructions to clone, set up, and run QueryMind on a Windows laptop or desktop.

### 1. Prerequisites

Before starting, ensure your system has:
* **Operating System**: Windows 10/11 (or Linux/macOS with equivalent shell commands)
* **Python**: Version `3.10` or `3.11` ([Download Python](https://www.python.org/downloads/))
* **Node.js & npm**: Node.js `v18+` or `v20+` ([Download Node.js](https://nodejs.org/))
* **Git**: Installed and configured ([Download Git](https://git-scm.com/))
* **Hardware**:
  * An NVIDIA GPU with CUDA support (e.g. RTX 3060, RTX 4060, or better with 8GB+ VRAM) is recommended to run local Qwen inference and LoRA fine-tuning.
  * If running on CPU or low-memory machine, the cloud **NVIDIA Nemotron API** path can run with zero local GPU requirements.

---

### 2. Clone the Repository

Open PowerShell or your terminal and clone the repository:

```powershell
git clone https://github.com/eng23cs0396-cell/T2SQL-new.git
cd T2SQL-new
```

---

### 3. Setup Python Backend Environment

1. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Install PyTorch with CUDA 12.1 support**:
   ```powershell
   pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
   ```

3. **Install the backend dependencies**:
   ```powershell
   pip install -r backend/requirements.txt
   ```

---

### 4. Setup Frontend Dependencies

Install the required npm packages for the Vite + React frontend:

```powershell
cd frontend
npm install
cd ..
```

---

### 5. Create `.env` & Configure NVIDIA API Key

The platform uses NVIDIA NIM API to run the high-speed Nemotron 3.5 Lightning model.

#### How to get a free NVIDIA API Key:
1. Go to [build.nvidia.com](https://build.nvidia.com).
2. Sign up or log in with your NVIDIA Developer account.
3. Search for the model: **`nvidia/nemotron-3.5-lightning-30b-a3b`**.
4. Click the green **"Get API Key"** button to generate your personal key (starts with `nvapi-...`).

#### Setting up the `.env` file:
In the project root folder, copy the example file to `.env`:

```powershell
copy backend\.env.example .env
```

Open `.env` in a text editor (e.g., Notepad, VS Code) and paste your API key:

```ini
NVIDIA_API_KEY=nvapi-your-actual-api-key-here
HOST=127.0.0.1
PORT=8000
```

> **Note**: `.env` is listed in `.gitignore` and is never committed to GitHub, keeping your key secure.

---

### 6. Start the Application (Automated Scripts)

We have provided ready-to-use PowerShell scripts in the root directory for single-command management:

#### Start the Platform:
```powershell
.\start.ps1
```
What `start.ps1` does:
* Launches the FastAPI backend server on `http://127.0.0.1:8000`.
* Launches the Vite + React frontend server on `http://localhost:5173`.
* Verifies both services are listening and healthy.
* Automatically opens `http://localhost:5173` in your default web browser!

#### Stop the Platform:
When you are done, run:
```powershell
.\stop.ps1
```
What `stop.ps1` does:
* Gracefully terminates the running Python (Uvicorn) backend on port `8000`.
* Gracefully terminates the Vite (Node) dev server on port `5173`.
* Frees up all ports cleanly.

---

### 7. Alternative: Running Manually (Two Terminals)

If you prefer viewing live terminal logs:

**Terminal 1 (Backend)**:
```powershell
.\.venv\Scripts\activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*API documentation is live at `http://127.0.0.1:8000/docs`*

**Terminal 2 (Frontend)**:
```powershell
cd frontend
npm run dev
```
*Web application opens at `http://localhost:5173`*

---

## Running the Empirical Benchmarks

To reproduce the benchmark on your local machine across all three models:

```powershell
.\.venv\Scripts\activate
python scripts/run_scale_complexity_benchmark.py --models nemotron,qwen_few_shot,qwen_lora --suite scored
```

Reports are automatically saved to:
* Latest run summary: [`outputs/evaluation/scale_complexity_latest.json`](outputs/evaluation/scale_complexity_latest.json)
* UI dashboard cache: [`outputs/evaluation/latest_evaluation_summary.json`](outputs/evaluation/latest_evaluation_summary.json)
* Formatted documentation: [`RESULTS.md`](RESULTS.md)

---

## Included Web Pages

1. **Overview**: Architectural diagram, design patterns, and research methodology.
2. **Playground**: Interactive interface with dynamic database selector (33 preloaded databases), schema viewer, model selector, query suggestions, and table preview.
3. **Model Comparison**: Side-by-side execution of Nemotron, Qwen Few-Shot, and Qwen LoRA on any selected database and question.
4. **Fine-Tuning Lab**: LoRA hyperparameter configuration console, parameter efficiency breakdown, and adapter status.
5. **Evaluation Dashboard**: Visual charts for SQL validity, execution accuracy, latency distribution, and per-query logs.
6. **Database Explorer**: Database switcher, table schema inspector, foreign key graph, and live table data browser.

---

## Project Structure

```
├── backend/                  # FastAPI REST API, model engines, and security
│   ├── api/routes.py         # Endpoints for inference, comparison, schema, eval
│   ├── database/             # Schema extractor, SQLite manager, SQL security
│   ├── models/               # Nemotron NIM client and local Qwen engine
│   └── evaluation/           # Metrics, evaluator, test case loaders
├── frontend/                 # Vite + React 19 single-page application
│   ├── src/components/       # Layout, Navigation, SchemaTree, SQLViewer
│   └── src/pages/            # Playground, Comparison, Evaluation, Lab, Explorer
├── data/
│   ├── databases/            # 33 domain SQLite databases (.db / .sqlite)
│   └── processed/            # Spider evaluation test splits (spider_test.json)
├── outputs/
│   ├── adapters/             # Trained Qwen LoRA PEFT adapter weights
│   └── evaluation/           # Generated evaluation reports (JSON / CSV)
├── scripts/                  # Standalone benchmark and dataset generation scripts
├── start.ps1                 # Single-click launcher for backend + frontend + browser
├── stop.ps1                  # Single-click service stopper
├── RESULTS.md                # Full empirical benchmark report and error analysis
└── README.md                 # Complete platform documentation and setup guide
```
