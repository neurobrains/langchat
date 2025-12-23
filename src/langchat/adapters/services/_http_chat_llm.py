# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import requests


@dataclass
class SimpleAIMessage:
    """
    Minimal response object compatible with how LangChat reads LLM results.
    """

    content: str


@dataclass
class HTTPChatLLM:
    """
    Minimal LangChain-ish chat model wrapper.

    It implements `.invoke()` and `.ainvoke()` and returns an object with `.content`,
    which is all LangChat uses in `UserSession`.
    """

    invoke_func: Callable[[list[Any]], str]

    def invoke(self, messages: list[Any]) -> Any:
        text = self.invoke_func(messages)
        return SimpleAIMessage(content=text)

    async def ainvoke(self, messages: list[Any]) -> Any:
        # Python 3.8-friendly async wrapper (avoid asyncio.to_thread typing issues)
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, messages)


def _messages_to_text(messages: list[Any]) -> str:
    # LangChat currently passes [HumanMessage(content=formatted_prompt)]
    if not messages:
        return ""
    last = messages[-1]
    if hasattr(last, "content"):
        return str(last.content)
    return str(last)


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_s: int = 60) -> Any:
    res = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    res.raise_for_status()
    return res.json()


