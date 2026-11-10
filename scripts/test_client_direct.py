import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
from backend.main import app
from fastapi.testclient import TestClient

t0 = time.time()
with TestClient(app) as client:
    print(f"TestClient initialized in {round(time.time() - t0, 3)}s")
    res = client.get("/api/health")
    print("Health:", res.json())
    res = client.get("/api/models")
    print("Models:", res.json())
    res = client.get("/api/database/list")
    print("Databases count:", len(res.json()))
