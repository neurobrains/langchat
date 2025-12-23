# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from itertools import cycle
from typing import Any

from langchat.adapters.base import LLMProvider
from langchat.adapters.logger import logger
from langchat.adapters.services._http_chat_llm import HTTPChatLLM, _messages_to_text, post_json


class AnthropicLLMService(LLMProvider):
    """
    Anthropic LLM service with optional API key rotation.

    Env var compatibility:
      - ANTHROPIC_API_KEY or ANTHROPIC_API_KEYS (comma-separated)
    """

    def __init__(
        self,
        model: str,
        temperature: float,
        api_keys: list[str],
        max_retries_per_key: int = 2,
        max_tokens: int = 1024,
    ):
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

        self.api_keys = cycle(api_keys) if api_keys else cycle([])
        self._current_key = next(self.api_keys) if api_keys else None
        self.max_retries = len(api_keys) * max_retries_per_key if api_keys else 0

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
    def current_key(self) -> str | None:
        return self._current_key

    def _rotate_key(self) -> None:
        self._current_key = next(self.api_keys)
        logger.info(f"Rotating to new Anthropic API key: {self._current_key[:8]}...")
        self._current_llm = self._create_llm()

    def _create_llm(self) -> HTTPChatLLM:
        if not self._current_key:
            raise ValueError("No Anthropic API keys provided")

        def _invoke(messages: list[Any]) -> str:
            prompt = _messages_to_text(messages)
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self._current_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "temperature": self._temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            data = post_json(url, headers=headers, payload=payload)
            # Response: { content: [{type:"text", text:"..."}], ... }
            content = data.get("content", [])
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict) and "text" in first:
                    return str(first["text"])
            return str(data)

        return HTTPChatLLM(invoke_func=_invoke)

    def invoke(self, messages: Any, **_kwargs: Any) -> Any:
        attempts = 0

        # Normalize to list for our HTTP wrapper
        msg_list = messages if isinstance(messages, list) else [messages]

        while attempts < max(1, self.max_retries):
            try:
                return self._current_llm.invoke(msg_list)
            except Exception as e:
                attempts += 1
                logger.warning(
                    f"Anthropic API call failed (attempt {attempts}/{max(1, self.max_retries)}): {str(e)}"
                )
                if attempts < max(1, self.max_retries) and self.max_retries > 0:
                    self._rotate_key()
                    continue
                raise


