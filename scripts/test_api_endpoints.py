"""
Automated Integration Test Suite for QueryMind API
Tests schema extraction, LangChain generation, SQL validation, execution, and health endpoints.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["status"] == "online"
    assert data["nemotron_configured"] is True
    assert data["database_count"] >= 2
    print("[PASS] GET /api/health:", data)

def test_models():
    res = client.get("/api/models")
    assert res.status_code == 200, f"Models check failed: {res.text}"
    data = res.json()
    assert len(data["models"]) == 2
    print("[PASS] GET /api/models:", [m["id"] for m in data["models"]])

def test_database_list_and_schema():
    res = client.get("/api/database/list")
    assert res.status_code == 200
    dbs = res.json()
    assert len(dbs) >= 2
    print(f"[PASS] GET /api/database/list: Found {len(dbs)} databases")

    db_id = dbs[0]["id"]
    schema_res = client.get(f"/api/database/{db_id}/schema")
    assert schema_res.status_code == 200
    schema_data = schema_res.json()
    assert "tables" in schema_data
    assert "formatted_text" in schema_data
    print(f"[PASS] GET /api/database/{db_id}/schema: {len(schema_data['tables'])} tables extracted")

def test_generate_and_execute_nemotron():
    payload = {
        "database_id": "university.db",
        "question": "What is the highest instructor salary?",
        "model": "nemotron",
        "technique": "zero_shot"
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200, f"Generate failed: {res.text}"
    data = res.json()
    assert data["validation"]["valid"] is True
    assert len(data["generated_sql"]) > 5
    assert data["execution"]["success"] is True
    print("[PASS] POST /api/generate (Nemotron):", data["generated_sql"], "| Result:", data["execution"]["rows"])

def test_sql_injection_defense():
    # Attempt harmful SQL mutation through executor
    res = client.post("/api/execute", json={"database_id": "university.db", "sql": "DROP TABLE students;"})
    # Should be rejected by SQLGlot / SQLite authorizer
    assert res.status_code == 400 or (res.status_code == 200 and res.json().get("success") is False)
    print("[PASS] Security Guardrail: DROP TABLE successfully blocked!")

def test_finetuning_preflight():
    res = client.post("/api/finetuning/preflight", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["can_train"] is True
    print("[PASS] POST /api/finetuning/preflight: Ready on", data["device_name"])

if __name__ == "__main__":
    print("Running integration tests against QueryMind API...")
    test_health()
    test_models()
    test_database_list_and_schema()
    test_generate_and_execute_nemotron()
    test_sql_injection_defense()
    test_finetuning_preflight()
    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
