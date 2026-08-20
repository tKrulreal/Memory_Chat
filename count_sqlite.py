import sqlite3
import os

db_path = os.path.join("data", "app.db")
conn = sqlite3.connect(db_path)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

for t in tables:
    table_name = t[0]
    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"{table_name}: {count}")
