"""Custom exceptions used in the project."""


class AgenticSQLError(Exception):
    """Base class for project exceptions."""


class UnsafeSQLError(AgenticSQLError):
    """Raised when SQL is not read-only."""


class LLMUnavailableError(AgenticSQLError):
    """Raised when LLM backend is unavailable."""
