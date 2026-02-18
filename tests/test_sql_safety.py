from agenticsql.db import validate_read_only_sql
from agenticsql.errors import UnsafeSQLError


def test_select_allowed():
    validate_read_only_sql("SELECT * FROM customers")


def test_with_allowed():
    validate_read_only_sql("WITH c AS (SELECT 1 AS x) SELECT * FROM c")


def test_insert_blocked():
    try:
        validate_read_only_sql("INSERT INTO customers(name) VALUES('x')")
    except UnsafeSQLError:
        return
    raise AssertionError("INSERT should be blocked")


def test_multi_statement_blocked():
    try:
        validate_read_only_sql("SELECT 1; SELECT 2")
    except UnsafeSQLError:
        return
    raise AssertionError("Multi statements should be blocked")
