# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Smoke tests for the new public API surface introduced in the providers refactor.

These tests verify that imports, re-exports, and the top-level namespace are
all correct — without making real network calls.
"""


# ---------------------------------------------------------------------------
# Package-level imports
# ---------------------------------------------------------------------------


class TestPackageImports:
    def test_version_is_set(self):
        import langchat

        assert hasattr(langchat, "__version__")
        assert langchat.__version__ == "1.0.2"

    def test_langchat_class_importable(self):
        from langchat import LangChat

        assert LangChat is not None

    def test_chat_response_importable_from_root(self):
        from langchat import ChatResponse

        assert ChatResponse is not None

    def test_providers_namespace_importable_from_root(self):
        from langchat import providers

        assert providers is not None

    def test_all_contains_expected_names(self):
        import langchat

        assert "LangChat" in langchat.__all__
        assert "ChatResponse" in langchat.__all__
        assert "providers" in langchat.__all__


# ---------------------------------------------------------------------------
# providers sub-module
# ---------------------------------------------------------------------------


class TestProvidersModule:
    def test_all_llm_providers_importable(self):
        from langchat.providers import Anthropic, Cohere, Gemini, Mistral, Ollama, OpenAI

        for cls in (OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama):
            assert cls is not None

    def test_pinecone_importable(self):
        from langchat.providers import Pinecone

        assert Pinecone is not None

    def test_supabase_importable(self):
        from langchat.providers import Supabase

        assert Supabase is not None

    def test_providers_all_is_complete(self):
        from langchat import providers

        expected = {
            "OpenAI",
            "Anthropic",
            "Gemini",
            "Mistral",
            "Cohere",
            "Ollama",
            "Pinecone",
            "Supabase",
        }
        assert expected.issubset(set(providers.__all__))

    def test_providers_accessible_via_root_namespace(self):
        import langchat

        assert hasattr(langchat.providers, "OpenAI")
        assert hasattr(langchat.providers, "Pinecone")
        assert hasattr(langchat.providers, "Supabase")


# ---------------------------------------------------------------------------
# ChatResponse type
# ---------------------------------------------------------------------------


class TestChatResponseType:
    def test_chat_response_is_dataclass(self):
        import dataclasses

        from langchat import ChatResponse

        assert dataclasses.is_dataclass(ChatResponse)

    def test_chat_response_instantiates_correctly(self):
        from langchat import ChatResponse

        r = ChatResponse(
            text="hello",
            user_id="alice",
            platform="default",
            status="success",
            response_time=0.5,
            timestamp="2025-01-01T00:00:00Z",
        )
        assert r.text == "hello"
        assert r.status == "success"
        assert r.error is None

    def test_chat_response_bool_protocol(self):
        from langchat import ChatResponse

        ok = ChatResponse(
            text="ok",
            user_id="u",
            platform="d",
            status="success",
            response_time=0.1,
            timestamp="t",
        )
        fail = ChatResponse(
            text="",
            user_id="u",
            platform="d",
            status="error",
            response_time=0.0,
            timestamp="t",
        )
        assert bool(ok) is True
        assert bool(fail) is False

    def test_chat_response_str_protocol(self):
        from langchat import ChatResponse

        r = ChatResponse(
            text="The answer.",
            user_id="u",
            platform="d",
            status="success",
            response_time=0.1,
            timestamp="t",
        )
        assert str(r) == "The answer."


# ---------------------------------------------------------------------------
# Backward compat — old adapter import paths still work
# ---------------------------------------------------------------------------


class TestBackwardCompatAdapterImports:
    """The old deep import paths must still work so existing code isn't broken."""

    def test_old_llm_import_path(self):
        from langchat.adapters.llm import (
            Anthropic,
            Cohere,
            Gemini,
            Mistral,
            Ollama,
            OpenAI,
        )

        for cls in (OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama):
            assert cls is not None

    def test_old_vector_db_import_path(self):
        from langchat.adapters.vector_db import Pinecone

        assert Pinecone is not None

    def test_old_database_import_path(self):
        from langchat.adapters.database import Supabase

        assert Supabase is not None


# ---------------------------------------------------------------------------
# LangChat SDK surface
# ---------------------------------------------------------------------------


class TestLangChatSurface:
    def _make_lc(self):
        from unittest.mock import MagicMock, patch

        from langchat import LangChat

        with patch("langchat.sdk.LangChatEngine"):
            return LangChat(llm=MagicMock(), vector_db=MagicMock(), db=MagicMock())

    def test_has_chat(self):
        lc = self._make_lc()
        assert callable(lc.chat)

    def test_has_chat_sync(self):
        lc = self._make_lc()
        assert callable(lc.chat_sync)

    def test_has_index(self):
        lc = self._make_lc()
        assert callable(lc.index)

    def test_has_get_session(self):
        lc = self._make_lc()
        assert callable(lc.get_session)

    def test_has_load_env(self):
        lc = self._make_lc()
        assert callable(lc.load_env)

    def test_chat_is_coroutine_function(self):
        import asyncio

        lc = self._make_lc()
        assert asyncio.iscoroutinefunction(lc.chat)

    def test_chat_sync_is_not_coroutine(self):
        import asyncio

        lc = self._make_lc()
        assert not asyncio.iscoroutinefunction(lc.chat_sync)
