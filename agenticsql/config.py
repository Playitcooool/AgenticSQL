"""Runtime configuration for AgenticSQL."""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("AGENTICSQL_MODEL", "qwen3:1.7b")
    ollama_base_url: str = os.getenv("AGENTICSQL_OLLAMA_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("AGENTICSQL_TEMPERATURE", "0"))
    max_rows: int = int(os.getenv("AGENTICSQL_MAX_ROWS", "200"))
    output_dir: str = os.getenv("AGENTICSQL_OUTPUT_DIR", "outputs")
