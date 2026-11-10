# QueryMind – Text-to-SQL LLM Platform

QueryMind turns a natural-language question and a SQLite database into a read-only SQL query, then runs that query and returns the rows. It compares two generation paths:

1. **NVIDIA Nemotron 3.5 Lightning** (`nvidia/nemotron-3.5-lightning-30b-a3b`) through the NVIDIA NIM API. This path needs a valid `NVIDIA_API_KEY`.
2. **Local Qwen2.5-Coder-3B-Instruct** on an NVIDIA GPU, in two modes: Spider few-shot prompting, and a rank-8 LoRA adapter.

Schemas are read from the database at request time. Generated SQL is parsed with SQLGlot and executed through a read-only SQLite connection.

---

## Architecture

```
            SQLite database                         Question
                    │                                   │
                    ▼                                   │
         Dynamic schema extractor                       │
         (sqlite_master, PRAGMA table_info,            │
          PRAGMA foreign_key_list)                      │
                    │                                   │
                    └──────────────┬────────────────────┘
                                   ▼
                    Nemotron API    or    local Qwen
                    (optional)           few-shot or LoRA
                                   │
                                   ▼
                         SQLGlot validator
                    single SELECT / WITH only
                                   │
                                   ▼
                    Read-only SQLite executor
                    (mode=ro, authorizer, row cap)
                                   │
                                   ▼
                         Vite + React frontend
```

---

## Evaluation & Benchmark Results

The evaluation suite benchmarks model performance across database schema complexities ranging from 3 to 12 tables (`veterinary_clinic`, `film_production`, `research_grants`, `maritime_shipping`), comparing:
- **NVIDIA Nemotron 3.5 Lightning** (Cloud API via NVIDIA NIM)
- **Local Qwen2.5-Coder-3B-Instruct (Few-Shot Prompting)**
- **Local Qwen2.5-Coder-3B-Instruct (Supervised PEFT LoRA Adapter)**

Detailed empirical benchmark results, accuracy metrics, error breakdowns, and per-case logs are tracked separately in [RESULTS.md](RESULTS.md).

To run or reproduce the benchmark across all models:

```powershell
.venv\Scripts\python.exe scripts/run_scale_complexity_benchmark.py --models nemotron,qwen_few_shot,qwen_lora --suite scored
```

---

## Databases

SQLite files live in `data/databases/`. The scale benchmark uses:

| File | Tables | Domain |
| :--- | ---: | :--- |
| `veterinary_clinic.db` | 3 | Clinics, veterinarians, visits |
| `film_production.db` | 9 | Studios, films, cast, genres, box office, awards |
| `research_grants.db` | 10 | Campuses, courses, grants, publications |
| `maritime_shipping.db` | 12 | Lines, vessels, voyages, cargo, crew, invoices |

The same folder also holds the earlier multi-table demos (hospital, banking, supply chain, airline, hotel, university, ecommerce, and others). Upload of `.db`, `.sqlite`, and `.sqlite3` files is supported from the UI.

---

## Models

### NVIDIA Nemotron 3.5 Lightning

- Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions`
- Settings: `temperature: 0.0`, `max_tokens: 512`, thinking disabled
- The API key is read from `.env` or `backend/.env` and is never sent to the frontend

### Local Qwen2.5-Coder-3B-Instruct

- Few-shot: up to 3 Spider training demonstrations selected for the question
- LoRA: adapter in `outputs/adapters/qwen_lora_spider` (rank 8, alpha 16, dropout 0.05, target modules `q_proj`, `k_proj`, `v_proj`, `o_proj`)
- Trainable parameters: 3,686,400 (0.1193% of the 3B model)
- The base weights stay frozen. The adapter is loaded on top with PEFT.

The fine-tune script and local inference engine are sized for an 8GB NVIDIA GPU (batch size 1, gradient accumulation 4, FP16, gradient checkpointing). See [RESULTS.md](RESULTS.md) for empirical evaluation metrics.

---

## SQL safety

- SQLGlot must parse exactly one `SELECT` or `WITH` statement.
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `ATTACH`, `DETACH`, and `PRAGMA` are rejected.
- SQLite is opened with `mode=ro` and an authorizer that denies writes.
- Execution is capped at 10 seconds and 100 rows.

Result comparison treats `NULL` as equal to `NULL`, compares floats with a `1e-4` tolerance, and requires row order to match only when the gold query contains `ORDER BY`.

---

## Setup

### Prerequisites

- Windows 10/11
- Python 3.10 or 3.11
- Node.js 18+
- An NVIDIA GPU with CUDA for local Qwen
- An NVIDIA NIM API key only if you want the Nemotron path

### 1. Environment

Copy the example env file and set the key if you have one:

```powershell
copy backend\.env.example .env
```

```ini
NVIDIA_API_KEY=nvapi-your-key-here
HOST=127.0.0.1
PORT=8000
```

### 2. Backend

```powershell
uv venv .venv --python 3.10
.venv\Scripts\activate
uv pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
uv pip install -r backend/requirements.txt
```

### 3. Dataset prep and fine-tuning

Spider splits, if you need to rebuild them:

```powershell
.venv\Scripts\python.exe backend/finetuning/prepare_dataset.py
```

Retrain the adapter:

```powershell
.venv\Scripts\python.exe scripts/run_finetuning.py
```

A trained adapter is already in `outputs/adapters/qwen_lora_spider`.

### 4. Run the app

Backend:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs: `http://127.0.0.1:8000/docs`

Frontend, in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

### 5. API smoke test

```powershell
.venv\Scripts\python.exe scripts/test_api_endpoints.py
```

---

## Frontend pages

1. **Overview** — architecture and method.
2. **Playground** — pick a database, inspect the schema, generate SQL, and view rows.
3. **Model comparison** — Nemotron, Qwen few-shot, and Qwen LoRA on the same question.
4. **Fine-tuning lab** — LoRA settings and adapter status.
5. **Evaluation** — validity, execution accuracy, latency, and per-question results.
6. **Database explorer** — tables, foreign keys, and sample rows.

---

## Project layout

```
backend/          FastAPI app, models, schema extraction, SQL guard, evaluation
frontend/         Vite + React UI
data/databases/   SQLite databases used by the UI and benchmarks
data/processed/   Prepared Spider splits and curated questions
scripts/          Benchmark, dataset, and fine-tune entry points
outputs/adapters/ Trained LoRA adapter
outputs/evaluation/ JSON and CSV benchmark reports
```

Further implementation notes are in [`PROJECT_IMPLEMENTATION_REPORT.md`](PROJECT_IMPLEMENTATION_REPORT.md).
