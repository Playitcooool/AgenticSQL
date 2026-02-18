import sqlite3
from pathlib import Path

from agenticsql.db import load_schema


def test_load_schema(tmp_path: Path):
    db = tmp_path / "demo.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    conn.commit()
    conn.close()

    schema = load_schema(str(db))
    assert "users" in schema.tables
    assert schema.tables["users"][0]["name"] == "id"
