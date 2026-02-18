"""LLM integration layer."""
from __future__ import annotations

from langchain_ollama import ChatOllama

from .config import Settings
from .errors import LLMUnavailableError


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm = ChatOllama(
            model=settings.model_name,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
        )

    def invoke_text(self, prompt: str) -> str:
        try:
            response = self._llm.invoke(prompt)
        except Exception as exc:
            raise LLMUnavailableError(
                "Failed to connect to Ollama. Ensure service is running and model is available."
            ) from exc
        content = str(response.content).strip()
        if not content:
            raise LLMUnavailableError("LLM returned empty response.")
        return content
