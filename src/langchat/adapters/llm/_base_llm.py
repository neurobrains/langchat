# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Base LLM classes for all providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class AIMessage:
    """Simple AI message response compatible with LangChain."""

    content: str


@dataclass
class BaseLLM:
    """
    Base LLM wrapper that implements invoke() and ainvoke().
    Compatible with LangChain's chat model interface.
    """

    invoke_func: Callable[[list[Any]], str]

    def invoke(self, messages: list[Any]) -> Any:
        """Synchronous invoke."""
        text = self.invoke_func(messages)
        return AIMessage(content=text)

    async def ainvoke(self, messages: list[Any]) -> Any:
        """Asynchronous invoke."""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, messages)


def messages_to_text(messages: list[Any]) -> str:
    """Extract text from messages list."""
    if not messages:
        return ""
    last = messages[-1]
    if hasattr(last, "content"):
        return str(last.content)
    return str(last)


__all__ = ["AIMessage", "BaseLLM", "messages_to_text"]
