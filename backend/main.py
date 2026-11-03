"""
QueryMind – Intelligent Text-to-SQL LLM Platform
FastAPI Application Entry Point
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load backend environment variables
load_dotenv()

from backend.api.routes import router as api_router

app = FastAPI(
    title="QueryMind API",
    description="Intelligent Text-to-SQL Platform comparing NVIDIA Nemotron 3.5 Lightning and Local Qwen2.5-Coder-3B-Instruct (Few-Shot & LoRA).",
    version="1.0.0"
)

# CORS configuration for React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "project": "QueryMind – Intelligent Text-to-SQL LLM Platform",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)

