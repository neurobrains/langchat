# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from itertools import cycle
from typing import Any

from langchat.adapters.base import LLMProvider
from langchat.adapters.services._http_chat_llm import HTTPChatLLM, _messages_to_text, post_json
from langchat.logger import logger


class GeminiLLMService(LLMProvider):
    """
    Google Gemini (Generative Language API) LLM service with optional key rotation.

    Env var compatibility:
      - GEMINI_API_KEY / GOOGLE_API_KEY or GEMINI_API_KEYS (comma-separated)
    """

    def __init__(
        self,
        model: str,
        temperature: float,
        api_keys: list[str],
        max_retries_per_key: int = 2,
    ):
        self._model = model
        self._temperature = temperature

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
        logger.info(f"Rotating to new Gemini API key: {self._current_key[:8]}...")
        self._current_llm = self._create_llm()

    def _create_llm(self) -> HTTPChatLLM:
        if not self._current_key:
            raise ValueError("No Gemini API keys provided")

        def _invoke(messages: list[Any]) -> str:
            prompt = _messages_to_text(messages)
            # https://ai.google.dev/api/rest/v1beta/models/generateContent
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/{self._model}:generateContent?key={self._current_key}"
            )
            headers = {"content-type": "application/json"}
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": self._temperature},
            }

            data = post_json(url, headers=headers, payload=payload)
            # candidates[0].content.parts[0].text
            candidates = data.get("candidates", [])
            if isinstance(candidates, list) and candidates:
                c0 = candidates[0]
                if isinstance(c0, dict):
                    content = c0.get("content", {})
                    if isinstance(content, dict):
                        parts = content.get("parts", [])
                        if isinstance(parts, list) and parts:
                            p0 = parts[0]
                            if isinstance(p0, dict) and "text" in p0:
                                return str(p0["text"])
            return str(data)

        return HTTPChatLLM(invoke_func=_invoke)

    def invoke(self, messages: Any, **_kwargs: Any) -> Any:
        attempts = 0

        msg_list = messages if isinstance(messages, list) else [messages]

        while attempts < max(1, self.max_retries):
            try:
                return self._current_llm.invoke(msg_list)
            except Exception as e:
                attempts += 1
                logger.warning(
                    f"Gemini API call failed (attempt {attempts}/{max(1, self.max_retries)}): {str(e)}"
                )
                if attempts < max(1, self.max_retries) and self.max_retries > 0:
                    self._rotate_key()
                    continue
                raise


