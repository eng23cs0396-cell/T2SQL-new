"""
Direct Unit and Route Handler Test Suite
Invokes FastAPI route handlers directly without loopback network socket overhead.
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath("."))
from backend.api import routes

async def run_tests():
    print("[1] Testing health_check()...")
    t0 = time.time()
    health = await routes.health_check()
    print(f" -> OK ({round(time.time() - t0, 3)}s):", health)
    assert health["status"] == "online"
    assert health["database_count"] >= 21

    print("[2] Testing list_models()...")
    t0 = time.time()
    models = routes.list_models()
    print(f" -> OK ({round(time.time() - t0, 3)}s):", [m["id"] for m in models["models"]])
    assert len(models["models"]) == 2

    print("[3] Testing list_databases()...")
    t0 = time.time()
    dbs = routes.list_databases()
    print(f" -> OK ({round(time.time() - t0, 3)}s): Found {len(dbs)} databases")
    assert len(dbs) == 29

    print("[4] Testing get_schema('university.db')...")
    t0 = time.time()
    schema = routes.get_schema("university.db")
    print(f" -> OK ({round(time.time() - t0, 3)}s): Tables: {list(schema['tables'].keys())}")
    assert "students" in schema["tables"]
    assert "departments" in schema["tables"]

    print("[5] Testing execute_query (harmless SELECT)...")
    t0 = time.time()
    exec_res = routes.execute_query(routes.ExecuteRequest(
        database_id="university.db",
        sql="SELECT department_name, budget FROM departments ORDER BY budget DESC LIMIT 2;"
    ))
    print(f" -> OK ({round(time.time() - t0, 3)}s): {exec_res['rows']}")
    assert exec_res["success"] is True
    assert len(exec_res["rows"]) == 2

    print("[6] Testing SQL Injection Guardrail (DROP TABLE)...")
    t0 = time.time()
    exec_blocked = routes.execute_query(routes.ExecuteRequest(
        database_id="university.db",
        sql="DROP TABLE students;"
    ))
    print(f" -> OK ({round(time.time() - t0, 3)}s): Blocked:", exec_blocked["success"] is False)
    assert exec_blocked["success"] is False

    print("[7] Testing finetuning_preflight()...")
    t0 = time.time()
    preflight = routes.get_finetuning_preflight()
    print(f" -> OK ({round(time.time() - t0, 3)}s): Can train: {preflight['can_train']} on {preflight['device_name']}")
    assert preflight["can_train"] is True

    print("\n" + "=" * 65)
    print("ALL ROUTE HANDLER TESTS PASSED IN SECONDS!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_tests())
