# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from langchat.adapters.base import HistoryStore, RerankerProvider, VectorStoreProvider


@dataclass
class _InMemoryResponse:
    data: list[dict[str, Any]] = field(default_factory=list)


class _InMemoryQuery:
    def __init__(self, table: _InMemoryTable):
        self._table = table
        self._select_fields: list[str] | None = None
        self._filters: list[tuple[str, Any]] = []
        self._order_key: str | None = None
        self._order_desc: bool = False
        self._limit: int | None = None

    def select(self, fields: str) -> _InMemoryQuery:
        self._select_fields = [f.strip() for f in fields.split(",") if f.strip()]
        return self

    def eq(self, key: str, value: Any) -> _InMemoryQuery:
        self._filters.append((key, value))
        return self

    def order(self, key: str, desc: bool = False) -> _InMemoryQuery:
        self._order_key = key
        self._order_desc = desc
        return self

    def limit(self, n: int) -> _InMemoryQuery:
        self._limit = n
        return self

    def execute(self) -> _InMemoryResponse:
        rows = list(self._table.rows)

        for key, value in self._filters:
            rows = [r for r in rows if r.get(key) == value]

        if self._order_key:
            rows.sort(key=lambda r: r.get(self._order_key), reverse=self._order_desc)

        if self._limit is not None:
            rows = rows[: self._limit]

        if self._select_fields:
            rows = [{k: r.get(k) for k in self._select_fields} for r in rows]

        return _InMemoryResponse(data=rows)

    def insert(self, payload: dict[str, Any]) -> _InMemoryQuery:
        self._table.rows.append(dict(payload))
        return self


class _InMemoryTable:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []

    def select(self, fields: str) -> _InMemoryQuery:
        return _InMemoryQuery(self).select(fields)

    def insert(self, payload: dict[str, Any]) -> _InMemoryQuery:
        return _InMemoryQuery(self).insert(payload)


class InMemorySupabaseClient:
    """
    Minimal subset of the Supabase client used by LangChat.
    """

    def __init__(self):
        self._tables: dict[str, _InMemoryTable] = {
            "chat_history": _InMemoryTable(),
            "request_metrics": _InMemoryTable(),
        }

    def table(self, name: str) -> _InMemoryTable:
        if name not in self._tables:
            self._tables[name] = _InMemoryTable()
        return self._tables[name]


class InMemoryHistoryStore(HistoryStore):
    """
    In-memory HistoryStore fallback (no Supabase required).
    """

    def __init__(self):
        self._client = InMemorySupabaseClient()

    @property
    def client(self) -> InMemorySupabaseClient:
        return self._client

    def check_tables_exist(self) -> bool:
        return True

    def get_create_tables_sql(self) -> str:
        return "-- In-memory history store: no SQL required\n"


class InMemoryIDManager:
    """
    Minimal ID manager used by UserSession.save_message (no Supabase required).
    """

    def __init__(self, client: InMemorySupabaseClient):
        self.client = client
        self.initialized = True

    def initialize(self) -> None:
        self.initialized = True

    def insert_with_retry(self, table_name: str, data: dict[str, Any]) -> Any:
        # Add a timestamp if missing (match DB behavior loosely)
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
        return self.client.table(table_name).insert(data).execute()


class NoopVectorAdapter(VectorStoreProvider):
    """
    Vector store fallback when Pinecone isn't configured.
    """

    class _EmptyRetriever:
        def invoke(self, query: str) -> list[Any]:  # noqa: ARG002
            return []

        def get_relevant_documents(self, query: str) -> list[Any]:  # noqa: ARG002
            return []

    def get_retriever(self, k: int = 5) -> Any:  # noqa: ARG002
        return self._EmptyRetriever()


class NoopRerankerAdapter(RerankerProvider):
    """
    Reranker fallback when reranking isn't configured/enabled.
    """

    def create_compression_retriever(self, base_retriever: Any) -> Any:
        return base_retriever


