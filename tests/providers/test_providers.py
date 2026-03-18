# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for langchat.providers — auto-env wrappers around adapter classes."""

from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clear_env(*keys):
    """Return a dict suitable for use with monkeypatch.delenv / os.environ pop."""
    return dict.fromkeys(keys)


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------


class TestOpenAIProvider:
    def test_explicit_key(self):
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI("gpt-4o", api_key="sk-explicit")
            assert p.model == "gpt-4o"
            assert p.current_key == "sk-explicit"

    def test_reads_env_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI()
            assert p.current_key == "sk-from-env"

    def test_default_model(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI()
            assert p.model == "gpt-4o-mini"

    def test_model_as_first_positional_arg(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI("gpt-4o")
            assert p.model == "gpt-4o"

    def test_raises_without_key_or_env(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from langchat.providers import OpenAI

        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            OpenAI()

    def test_temperature_kwarg(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI("gpt-4o", temperature=0.2)
            assert p.temperature == 0.2

    def test_multiple_keys_rotation(self):
        with patch("langchat.adapters.llm.openai_provider.ChatOpenAI"):
            from langchat.providers import OpenAI

            p = OpenAI(api_keys=["sk-a", "sk-b"])
            assert p.current_key in ("sk-a", "sk-b")


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------


class TestAnthropicProvider:
    def test_explicit_key(self):
        from langchat.providers import Anthropic

        p = Anthropic(api_key="sk-ant-test")
        assert p.model == "claude-3-5-sonnet-20241022"
        assert p.current_key == "sk-ant-test"

    def test_reads_env_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-env")
        from langchat.providers import Anthropic

        p = Anthropic()
        assert p.current_key == "sk-ant-env"

    def test_model_as_first_positional_arg(self):
        from langchat.providers import Anthropic

        p = Anthropic("claude-opus-4-6", api_key="sk-ant-test")
        assert p.model == "claude-opus-4-6"

    def test_raises_without_key_or_env(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        from langchat.providers import Anthropic

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            Anthropic()

    def test_max_tokens_kwarg(self):
        from langchat.providers import Anthropic

        p = Anthropic(api_key="sk-ant-test", max_tokens=1024)
        assert p._max_tokens == 1024


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------


class TestGeminiProvider:
    def test_explicit_key(self):
        from langchat.providers import Gemini

        p = Gemini(api_key="gm-test")
        assert p.model == "gemini-1.5-flash"

    def test_reads_gemini_env_key(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "gm-env")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        from langchat.providers import Gemini

        p = Gemini()
        assert p.current_key == "gm-env"

    def test_reads_google_api_key_fallback(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-env")
        from langchat.providers import Gemini

        p = Gemini()
        assert p.current_key == "goog-env"

    def test_raises_without_key_or_env(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        from langchat.providers import Gemini

        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            Gemini()

    def test_model_as_first_positional_arg(self):
        from langchat.providers import Gemini

        p = Gemini("gemini-1.5-pro", api_key="gm-test")
        assert p.model == "gemini-1.5-pro"


# ---------------------------------------------------------------------------
# Mistral
# ---------------------------------------------------------------------------


class TestMistralProvider:
    def test_explicit_key(self):
        from langchat.providers import Mistral

        p = Mistral(api_key="ms-test")
        assert p.model == "mistral-small-latest"

    def test_reads_env_key(self, monkeypatch):
        monkeypatch.setenv("MISTRAL_API_KEY", "ms-env")
        from langchat.providers import Mistral

        p = Mistral()
        assert p.current_key == "ms-env"

    def test_raises_without_key_or_env(self, monkeypatch):
        monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
        from langchat.providers import Mistral

        with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
            Mistral()

    def test_model_as_first_positional_arg(self):
        from langchat.providers import Mistral

        p = Mistral("mistral-large-latest", api_key="ms-test")
        assert p.model == "mistral-large-latest"


# ---------------------------------------------------------------------------
# Cohere
# ---------------------------------------------------------------------------


class TestCohereProvider:
    def test_explicit_key(self):
        from langchat.providers import Cohere

        p = Cohere(api_key="co-test")
        assert p.model == "command"

    def test_reads_env_key(self, monkeypatch):
        monkeypatch.setenv("COHERE_API_KEY", "co-env")
        from langchat.providers import Cohere

        p = Cohere()
        assert p.current_key == "co-env"

    def test_raises_without_key_or_env(self, monkeypatch):
        monkeypatch.delenv("COHERE_API_KEY", raising=False)
        from langchat.providers import Cohere

        with pytest.raises(ValueError, match="COHERE_API_KEY"):
            Cohere()

    def test_model_as_first_positional_arg(self):
        from langchat.providers import Cohere

        p = Cohere("command-r", api_key="co-test")
        assert p.model == "command-r"


# ---------------------------------------------------------------------------
# Ollama (no API key required)
# ---------------------------------------------------------------------------


class TestOllamaProvider:
    def test_default_model(self):
        from langchat.providers import Ollama

        p = Ollama()
        assert p.model == "llama2"
        assert p.temperature == 0.7

    def test_model_as_first_positional_arg(self):
        from langchat.providers import Ollama

        p = Ollama("mistral")
        assert p.model == "mistral"

    def test_custom_base_url(self):
        from langchat.providers import Ollama

        p = Ollama(base_url="http://gpu-server:11434")
        assert p._base_url == "http://gpu-server:11434"

    def test_temperature_kwarg(self):
        from langchat.providers import Ollama

        p = Ollama(temperature=0.1)
        assert p.temperature == 0.1

    def test_no_api_key_needed(self, monkeypatch):
        """Ollama should never require an API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from langchat.providers import Ollama

        # Should not raise
        Ollama()


# ---------------------------------------------------------------------------
# Pinecone
# ---------------------------------------------------------------------------


class TestPineconeProvider:
    def _mock_pinecone(self):
        """Context managers to mock out network calls during init."""
        return (
            patch("langchat.adapters.vector_db.pinecone_adapter.Pinecone"),
            patch("langchat.adapters.vector_db.pinecone_adapter.OpenAIEmbeddings"),
            patch("langchat.adapters.vector_db.pinecone_adapter.PineconeVectorStore"),
        )

    def test_index_as_first_positional_arg(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        pc_mock, emb_mock, vs_mock = self._mock_pinecone()
        with pc_mock, emb_mock, vs_mock:
            from langchat.providers import Pinecone

            p = Pinecone("my-index")
            assert p.index_name == "my-index"

    def test_reads_pinecone_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-from-env")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        pc_mock, emb_mock, vs_mock = self._mock_pinecone()
        with pc_mock, emb_mock, vs_mock:
            from langchat.providers import Pinecone

            p = Pinecone("my-index")
            assert p.api_key == "pc-from-env"

    def test_reads_embedding_key_from_openai_env(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-embed-env")
        pc_mock, emb_mock, vs_mock = self._mock_pinecone()
        with pc_mock, emb_mock, vs_mock:
            from langchat.providers import Pinecone

            p = Pinecone("my-index")
            assert p.embedding_api_key == "sk-embed-env"

    def test_explicit_keys_override_env(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-env")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        pc_mock, emb_mock, vs_mock = self._mock_pinecone()
        with pc_mock, emb_mock, vs_mock:
            from langchat.providers import Pinecone

            p = Pinecone("idx", api_key="pc-explicit", embedding_api_key="sk-explicit")
            assert p.api_key == "pc-explicit"
            assert p.embedding_api_key == "sk-explicit"

    def test_raises_without_pinecone_key(self, monkeypatch):
        monkeypatch.delenv("PINECONE_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        from langchat.providers import Pinecone

        with pytest.raises(ValueError, match="PINECONE_API_KEY"):
            Pinecone("my-index")

    def test_raises_without_embedding_key(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-test")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from langchat.providers import Pinecone

        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            Pinecone("my-index")

    def test_custom_embedding_model(self, monkeypatch):
        monkeypatch.setenv("PINECONE_API_KEY", "pc-test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        pc_mock, emb_mock, vs_mock = self._mock_pinecone()
        with pc_mock, emb_mock, vs_mock:
            from langchat.providers import Pinecone

            p = Pinecone("my-index", embedding_model="text-embedding-3-small")
            assert p.embedding_model == "text-embedding-3-small"


# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------


class TestSupabaseProvider:
    def test_reads_url_and_key_from_env(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "supa-key")
        with patch("langchat.adapters.database.supabase_adapter.create_client"):
            from langchat.providers import Supabase

            p = Supabase()
            assert p.url == "https://test.supabase.co"
            assert p.key == "supa-key"

    def test_explicit_url_and_key(self):
        with patch("langchat.adapters.database.supabase_adapter.create_client"):
            from langchat.providers import Supabase

            p = Supabase(url="https://explicit.supabase.co", key="explicit-key")
            assert p.url == "https://explicit.supabase.co"
            assert p.key == "explicit-key"

    def test_reads_service_role_key_as_fallback(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
        with patch("langchat.adapters.database.supabase_adapter.create_client"):
            from langchat.providers import Supabase

            p = Supabase()
            assert p.key == "service-role-key"

    def test_raises_without_url(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_KEY", "supa-key")
        from langchat.providers import Supabase

        with pytest.raises(ValueError, match="SUPABASE_URL"):
            Supabase()

    def test_raises_without_key(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        from langchat.providers import Supabase

        with pytest.raises(ValueError, match="SUPABASE_KEY"):
            Supabase()


# ---------------------------------------------------------------------------
# __all__ completeness
# ---------------------------------------------------------------------------


def test_providers_all_exports():
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


def test_providers_importable_directly():
    from langchat.providers import (
        Anthropic,
        Cohere,
        Gemini,
        Mistral,
        Ollama,
        OpenAI,
        Pinecone,
        Supabase,
    )

    for cls in (OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama, Pinecone, Supabase):
        assert cls is not None
