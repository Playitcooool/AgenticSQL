"""Database utilities and SQL safety checks."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
from typing import Any

import pandas as pd

from .errors import UnsafeSQLError

READ_ONLY_PREFIXES = ("select", "with", "pragma")
FORBIDDEN_SQL_PATTERNS = (
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\bcreate\b",
    r"\battach\b",
    r"\bdetach\b",
    r"\bpragma\s+.*=",
)


@dataclass(frozen=True)
class QueryResult:
    sql: str
    rows: int
    dataframe: pd.DataFrame


@dataclass(frozen=True)
class SchemaInfo:
    tables: dict[str, list[dict[str, Any]]]

    def render_for_prompt(self) -> str:
        lines: list[str] = []
        for table, columns in self.tables.items():
            lines.append(f"Table: {table}")
            for col in columns:
                lines.append(
                    f"  - {col['name']} ({col['type']})"
                    + (" PRIMARY KEY" if col["pk"] else "")
                    + (" NOT NULL" if col["notnull"] else "")
                )
            lines.append("")
        return "\n".join(lines).strip()


def validate_read_only_sql(sql: str) -> None:
    sql_clean = sql.strip().strip(";")
    if not sql_clean:
        raise UnsafeSQLError("SQL is empty.")

    lower = sql_clean.lower()
    if ";" in sql_clean:
        raise UnsafeSQLError("Only a single SQL statement is allowed.")
    if not lower.startswith(READ_ONLY_PREFIXES):
        raise UnsafeSQLError("Only read-only SQL statements are allowed.")

    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(pattern, lower):
            raise UnsafeSQLError(f"Unsafe SQL detected: pattern `{pattern}`.")


def ensure_db_exists(db_path: str) -> Path:
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    return path


def load_schema(db_path: str) -> SchemaInfo:
    path = ensure_db_exists(db_path)
    conn = sqlite3.connect(path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]

        schema: dict[str, list[dict[str, Any]]] = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            schema[table] = [
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default": col[4],
                    "pk": bool(col[5]),
                }
                for col in cursor.fetchall()
            ]

        return SchemaInfo(tables=schema)
    finally:
        conn.close()


def run_query(db_path: str, sql: str, max_rows: int = 200) -> QueryResult:
    validate_read_only_sql(sql)
    path = ensure_db_exists(db_path)
    conn = sqlite3.connect(path)
    try:
        dataframe = pd.read_sql_query(sql, conn)
        if len(dataframe) > max_rows:
            dataframe = dataframe.head(max_rows)
        return QueryResult(sql=sql, rows=len(dataframe), dataframe=dataframe)
    finally:
        conn.close()


def dataframe_preview(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "(no rows)"
    return df.head(max_rows).to_markdown(index=False)
