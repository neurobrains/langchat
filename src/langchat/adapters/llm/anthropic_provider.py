# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Anthropic Claude LLM Provider."""

from __future__ import annotations

from itertools import cycle
from typing import Any

import requests

from langchat.adapters.llm._base_llm import BaseLLM, messages_to_text
from langchat.adapters.logger import logger


class Anthropic:
    """
    Anthropic Claude LLM provider with key rotation.

    Supports Claude 3.5 Sonnet, Claude 3 Opus, Haiku, and other models.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 1.0,
        max_retries_per_key: int = 2,
        max_tokens: int = 4096,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Single Anthropic API key (or use api_keys for multiple)
            api_keys: List of Anthropic API keys for rotation
            model: Claude model name (e.g., "claude-3-5-sonnet-20241022")
            temperature: Model temperature (0.0 to 1.0)
            max_retries_per_key: Maximum retries per API key
            max_tokens: Maximum tokens to generate
        """
        if api_key:
            api_keys = [api_key]
        if not api_keys:
            raise ValueError("At least one Anthropic API key is required (use api_key or api_keys)")

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self.api_keys = cycle(api_keys)
        self._current_key = next(self.api_keys)
        self.max_retries = len(api_keys) * max_retries_per_key
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

    @property
    def current_key(self) -> str:
        return self._current_key

    def _rotate_key(self) -> None:
        self._current_key = next(self.api_keys)
        logger.info(f"Rotating to new Anthropic API key: {self._current_key[:8]}...")
        self._current_llm = self._create_llm()

    def _create_llm(self) -> BaseLLM:
        def _invoke(messages: list[Any]) -> str:
            prompt = messages_to_text(messages)
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self._current_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "temperature": self._temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            res = requests.post(url, headers=headers, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()

            content = data.get("content", [])
            if content and "text" in content[0]:
                return str(content[0]["text"])
            return str(data)

        return BaseLLM(invoke_func=_invoke)

    def invoke(self, messages: Any) -> Any:
        attempts = 0
        msg_list = messages if isinstance(messages, list) else [messages]

        while attempts < max(1, self.max_retries):
            try:
                return self._current_llm.invoke(msg_list)
            except Exception as e:
                attempts += 1
                logger.warning(
                    f"Anthropic API call failed (attempt {attempts}/{max(1, self.max_retries)}): {str(e)}"
                )
                if attempts < max(1, self.max_retries):
                    self._rotate_key()
                    continue
                raise


__all__ = ["Anthropic"]
