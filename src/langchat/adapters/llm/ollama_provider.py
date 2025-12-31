# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Ollama LLM Provider for local/self-hosted models."""

from __future__ import annotations

from typing import Any

import requests

from langchat.adapters.llm._base_llm import BaseLLM, messages_to_text
from langchat.adapters.logger import logger


class Ollama:
    """
    Ollama LLM provider for running local open-source models.

    Supports Llama 2, Mistral, CodeLlama, and other Ollama models.
    """

    def __init__(
        self,
        model: str = "llama2",
        temperature: float = 0.7,
        base_url: str = "http://localhost:11434",
        options: dict | None = None,
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Ollama model name (e.g., "llama2", "mistral", "codellama")
            temperature: Model temperature (0.0 to 2.0)
            base_url: Ollama server URL
            options: Additional Ollama options (num_predict, top_k, etc.)
        """
        self._model = model
        self._temperature = temperature
        self._base_url = base_url.rstrip("/")
        self._options = options or {}
        self._current_llm = self._create_llm()

    @property
    def model(self) -> str:
        return self._model

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def current_llm(self) -> Any:
        return self._current_llm

    def _create_llm(self) -> BaseLLM:
        def _invoke(messages: list[Any]) -> str:
            prompt = messages_to_text(messages)
            url = f"{self._base_url}/api/generate"

            payload = {
                "model": self._model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": self._temperature, **self._options},
            }

            try:
                res = requests.post(url, json=payload, timeout=120)
                res.raise_for_status()
                data = res.json()
                return data.get("response", str(data))
            except requests.exceptions.ConnectionError as err:
                raise ConnectionError(
                    f"Could not connect to Ollama at {self._base_url}. "
                    f"Make sure Ollama is running (ollama serve). Error: {err}"
                ) from err

        return BaseLLM(invoke_func=_invoke)

    def invoke(self, messages: Any) -> Any:
        msg_list = messages if isinstance(messages, list) else [messages]

        try:
            return self._current_llm.invoke(msg_list)
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise


__all__ = ["Ollama"]
