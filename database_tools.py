"""
Database tools for AgenticSQL
"""
import sqlite3
from typing import List, Dict, Any
import pandas as pd
from langchain_core.tools import tool


@tool
def list_tables(db_path: str) -> str:
    """
    List all tables in the database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        A formatted string listing all tables with their schemas
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        result = "Database Tables:\n\n"

        for table in tables:
            table_name = table[0]
            result += f"Table: {table_name}\n"

            # Get schema for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            result += "Columns:\n"
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                result += f"  - {col_name} ({col_type})\n"
            result += "\n"

        conn.close()
        return result
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@tool
def execute_sql(db_path: str, sql_query: str) -> str:
    """
    Execute a SQL query and return the results.

    Args:
        db_path: Path to the SQLite database file
        sql_query: The SQL query to execute

    Returns:
        Query results as a formatted string
    """
    try:
        conn = sqlite3.connect(db_path)

        # Execute query and get results as DataFrame
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        if df.empty:
            return "Query executed successfully but returned no results."

        # Format results as string
        result = f"Query Results ({len(df)} rows):\n\n"
        result += df.to_string(index=False)

        return result
    except Exception as e:
        return f"Error executing SQL: {str(e)}"


def execute_sql_for_viz(db_path: str, sql_query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as DataFrame for visualization.

    Args:
        db_path: Path to the SQLite database file
        sql_query: The SQL query to execute

    Returns:
        Query results as pandas DataFrame
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Error executing SQL for visualization: {str(e)}")
