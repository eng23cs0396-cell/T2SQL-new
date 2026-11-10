import os
import sqlite3

db_dir = "data/databases"
for f in sorted(os.listdir(db_dir)):
    if f.endswith((".db", ".sqlite")):
        p = os.path.join(db_dir, f)
        con = sqlite3.connect(p)
        res = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        tables = [r[0] for r in res]
        print(f"{f:<32} ({len(tables)} tables): {', '.join(tables)}")
