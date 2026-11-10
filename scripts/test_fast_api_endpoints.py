"""
Fast API endpoints test (Health, Models, Database List, Schema, SQL Injection Guardrails, Finetuning Preflight)
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("[1] Testing /api/health...")
t0 = time.time()
res = client.get("/api/health")
assert res.status_code == 200
print(f" -> OK ({round(time.time() - t0, 3)}s): {res.json()}")

print("[2] Testing /api/models...")
t0 = time.time()
res = client.get("/api/models")
assert res.status_code == 200
print(f" -> OK ({round(time.time() - t0, 3)}s): {[m['id'] for m in res.json()['models']]}")

print("[3] Testing /api/database/list...")
t0 = time.time()
res = client.get("/api/database/list")
assert res.status_code == 200
dbs = res.json()
print(f" -> OK ({round(time.time() - t0, 3)}s): Found {len(dbs)} databases")

print("[4] Testing /api/database/{id}/schema...")
t0 = time.time()
res = client.get("/api/database/university.db/schema")
assert res.status_code == 200
print(f" -> OK ({round(time.time() - t0, 3)}s): Extracted {len(res.json()['tables'])} tables")

print("[5] Testing /api/execute (SQL injection protection)...")
t0 = time.time()
res = client.post("/api/execute", json={"database_id": "university.db", "sql": "DROP TABLE students;"})
assert res.status_code == 400 or (res.status_code == 200 and not res.json().get("success"))
print(f" -> OK ({round(time.time() - t0, 3)}s): Blocked unauthorized mutation successfully")

print("[6] Testing /api/finetuning/preflight...")
t0 = time.time()
res = client.post("/api/finetuning/preflight", json={})
assert res.status_code == 200
print(f" -> OK ({round(time.time() - t0, 3)}s): Ready on {res.json().get('device_name')}")

print("\nALL FAST API ENDPOINTS TESTED AND PASSED IN SECONDS!")
