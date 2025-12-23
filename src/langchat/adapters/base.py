# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    """
    Minimal interface LangChat expects from an LLM provider wrapper.
    """

    @property
    def current_llm(self) -> Any: ...


class VectorStoreProvider(Protocol):
    """
    Minimal interface for vector store adapter.
    """

    def get_retriever(self, k: int = 5) -> Any: ...


class RerankerProvider(Protocol):
    """
    Minimal interface for reranker adapter.
    """

    def create_compression_retriever(self, base_retriever: Any) -> Any: ...


class HistoryStore(Protocol):
    """
    Minimal interface for history store adapter (Supabase wrapper).
    """

    @property
    def client(self) -> Any: ...


__all__ = [
    "HistoryStore",
    "LLMProvider",
    "RerankerProvider",
    "VectorStoreProvider",
]


