# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
langchat.providers — clean, auto-env provider classes.

All providers automatically read credentials from environment variables
when no explicit key is passed, so you never have to repeat yourself.

Usage::

    from langchat import LangChat
    from langchat.providers import OpenAI, Pinecone, Supabase

    lc = LangChat(
        llm=OpenAI("gpt-4o"),
        vector_db=Pinecone("my-index"),
        db=Supabase(),
    )

Environment variables read automatically:

    OPENAI_API_KEY      — for OpenAI LLM and Pinecone embeddings
    ANTHROPIC_API_KEY   — for Anthropic Claude
    GEMINI_API_KEY      — for Google Gemini  (also: GOOGLE_API_KEY)
    MISTRAL_API_KEY     — for Mistral AI
    COHERE_API_KEY      — for Cohere
    PINECONE_API_KEY    — for Pinecone vector store
    SUPABASE_URL        — for Supabase
    SUPABASE_KEY        — for Supabase  (also: SUPABASE_SERVICE_ROLE_KEY)
"""

from __future__ import annotations

import os

from langchat.adapters.database.supabase_adapter import SupabaseAdapter as _SupabaseBase
from langchat.adapters.llm.anthropic_provider import Anthropic as _AnthropicBase
from langchat.adapters.llm.cohere_provider import Cohere as _CohereBase
from langchat.adapters.llm.gemini_provider import Gemini as _GeminiBase
from langchat.adapters.llm.mistral_provider import Mistral as _MistralBase
from langchat.adapters.llm.ollama_provider import Ollama as _OllamaBase
from langchat.adapters.llm.openai_provider import OpenAI as _OpenAIBase
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter as _PineconeBase

# ---------------------------------------------------------------------------
# LLM providers
# ---------------------------------------------------------------------------


class OpenAI(_OpenAIBase):
    """OpenAI LLM provider.

    Reads ``OPENAI_API_KEY`` from the environment automatically.

    Args:
        model: Model name (default: ``"gpt-4o-mini"``).
        api_key: Explicit API key — overrides the environment variable.
        api_keys: Multiple keys for automatic rotation.
        temperature: Sampling temperature (default: ``1.0``).
        max_retries_per_key: Retries before rotating to the next key.

    Examples::

        OpenAI()                          # env: OPENAI_API_KEY
        OpenAI("gpt-4o")
        OpenAI("gpt-4o", temperature=0.2)
        OpenAI(api_keys=["sk-1", "sk-2"]) # key rotation
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        *,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        temperature: float = 1.0,
        max_retries_per_key: int = 2,
    ):
        if not api_key and not api_keys:
            env_key = os.getenv("OPENAI_API_KEY")
            if not env_key:
                raise ValueError(
                    "OpenAI API key not found. "
                    "Set the OPENAI_API_KEY environment variable or pass api_key='sk-...'."
                )
            api_key = env_key

        super().__init__(
            api_key=api_key,
            api_keys=api_keys,
            model=model,
            temperature=temperature,
            max_retries_per_key=max_retries_per_key,
        )


class Anthropic(_AnthropicBase):
    """Anthropic Claude LLM provider.

    Reads ``ANTHROPIC_API_KEY`` from the environment automatically.

    Args:
        model: Model name (default: ``"claude-3-5-sonnet-20241022"``).
        api_key: Explicit API key — overrides the environment variable.
        api_keys: Multiple keys for automatic rotation.
        temperature: Sampling temperature (default: ``1.0``).
        max_tokens: Maximum tokens to generate (default: ``4096``).

    Examples::

        Anthropic()
        Anthropic("claude-opus-4-6")
        Anthropic("claude-haiku-4-5-20251001", temperature=0.5)
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        *,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        temperature: float = 1.0,
        max_retries_per_key: int = 2,
        max_tokens: int = 4096,
    ):
        if not api_key and not api_keys:
            env_key = os.getenv("ANTHROPIC_API_KEY")
            if not env_key:
                raise ValueError(
                    "Anthropic API key not found. "
                    "Set the ANTHROPIC_API_KEY environment variable or pass api_key='sk-ant-...'."
                )
            api_key = env_key

        super().__init__(
            api_key=api_key,
            api_keys=api_keys,
            model=model,
            temperature=temperature,
            max_retries_per_key=max_retries_per_key,
            max_tokens=max_tokens,
        )


class Gemini(_GeminiBase):
    """Google Gemini LLM provider.

    Reads ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``) from the environment automatically.

    Args:
        model: Model name (default: ``"gemini-1.5-flash"``).
        api_key: Explicit API key — overrides the environment variable.
        api_keys: Multiple keys for automatic rotation.
        temperature: Sampling temperature (default: ``1.0``).

    Examples::

        Gemini()
        Gemini("gemini-1.5-pro")
        Gemini("gemini-1.5-flash", temperature=0.3)
    """

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        *,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        temperature: float = 1.0,
        max_retries_per_key: int = 2,
    ):
        if not api_key and not api_keys:
            env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not env_key:
                raise ValueError(
                    "Gemini API key not found. "
                    "Set the GEMINI_API_KEY environment variable or pass api_key='...'."
                )
            api_key = env_key

        super().__init__(
            api_key=api_key,
            api_keys=api_keys,
            model=model,
            temperature=temperature,
            max_retries_per_key=max_retries_per_key,
        )


class Mistral(_MistralBase):
    """Mistral AI LLM provider.

    Reads ``MISTRAL_API_KEY`` from the environment automatically.

    Args:
        model: Model name (default: ``"mistral-small-latest"``).
        api_key: Explicit API key — overrides the environment variable.
        api_keys: Multiple keys for automatic rotation.
        temperature: Sampling temperature (default: ``0.7``).
        max_tokens: Maximum tokens to generate (default: ``4096``).

    Examples::

        Mistral()
        Mistral("mistral-large-latest")
        Mistral("mistral-small-latest", temperature=0.4)
    """

    def __init__(
        self,
        model: str = "mistral-small-latest",
        *,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        temperature: float = 0.7,
        max_retries_per_key: int = 2,
        max_tokens: int = 4096,
    ):
        if not api_key and not api_keys:
            env_key = os.getenv("MISTRAL_API_KEY")
            if not env_key:
                raise ValueError(
                    "Mistral API key not found. "
                    "Set the MISTRAL_API_KEY environment variable or pass api_key='...'."
                )
            api_key = env_key

        super().__init__(
            api_key=api_key,
            api_keys=api_keys,
            model=model,
            temperature=temperature,
            max_retries_per_key=max_retries_per_key,
            max_tokens=max_tokens,
        )


class Cohere(_CohereBase):
    """Cohere LLM provider.

    Reads ``COHERE_API_KEY`` from the environment automatically.

    Args:
        model: Model name (default: ``"command"``).
        api_key: Explicit API key — overrides the environment variable.
        api_keys: Multiple keys for automatic rotation.
        temperature: Sampling temperature (default: ``0.7``).
        max_tokens: Maximum tokens to generate (default: ``4096``).

    Examples::

        Cohere()
        Cohere("command-r")
        Cohere("command-light", temperature=0.5)
    """

    def __init__(
        self,
        model: str = "command",
        *,
        api_key: str | None = None,
        api_keys: list[str] | None = None,
        temperature: float = 0.7,
        max_retries_per_key: int = 2,
        max_tokens: int = 4096,
    ):
        if not api_key and not api_keys:
            env_key = os.getenv("COHERE_API_KEY")
            if not env_key:
                raise ValueError(
                    "Cohere API key not found. "
                    "Set the COHERE_API_KEY environment variable or pass api_key='...'."
                )
            api_key = env_key

        super().__init__(
            api_key=api_key,
            api_keys=api_keys,
            model=model,
            temperature=temperature,
            max_retries_per_key=max_retries_per_key,
            max_tokens=max_tokens,
        )


class Ollama(_OllamaBase):
    """Ollama provider for local / self-hosted models. No API key required.

    Args:
        model: Ollama model name (default: ``"llama2"``).
        temperature: Sampling temperature (default: ``0.7``).
        base_url: Ollama server URL (default: ``"http://localhost:11434"``).
        options: Extra Ollama generation options (``num_predict``, ``top_k``, …).

    Examples::

        Ollama()                           # uses llama2 at localhost:11434
        Ollama("mistral")
        Ollama("codellama", temperature=0.1)
        Ollama("llama2", base_url="http://gpu-server:11434")
    """

    def __init__(
        self,
        model: str = "llama2",
        *,
        temperature: float = 0.7,
        base_url: str = "http://localhost:11434",
        options: dict | None = None,
    ):
        super().__init__(
            model=model,
            temperature=temperature,
            base_url=base_url,
            options=options,
        )


# ---------------------------------------------------------------------------
# Vector database providers
# ---------------------------------------------------------------------------


class Pinecone(_PineconeBase):
    """Pinecone vector database provider.

    Reads ``PINECONE_API_KEY`` and ``OPENAI_API_KEY`` (for embeddings) from
    the environment automatically.

    Args:
        index: Pinecone index name **(required)**.
        api_key: Pinecone API key — overrides ``PINECONE_API_KEY``.
        embedding_api_key: OpenAI key for embeddings — overrides ``OPENAI_API_KEY``.
        embedding_model: Embedding model (default: ``"text-embedding-3-large"``).

    Examples::

        Pinecone("my-index")
        Pinecone("my-index", embedding_model="text-embedding-3-small")
        Pinecone("my-index", api_key="pc-...", embedding_api_key="sk-...")
    """

    def __init__(
        self,
        index: str,
        *,
        api_key: str | None = None,
        embedding_api_key: str | None = None,
        embedding_model: str = "text-embedding-3-large",
    ):
        if not api_key:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Pinecone API key not found. "
                    "Set the PINECONE_API_KEY environment variable or pass api_key='pc-...'."
                )

        if not embedding_api_key:
            embedding_api_key = os.getenv("OPENAI_API_KEY")
            if not embedding_api_key:
                raise ValueError(
                    "OpenAI API key required for Pinecone embeddings. "
                    "Set the OPENAI_API_KEY environment variable or pass embedding_api_key='sk-...'."
                )

        super().__init__(
            api_key=api_key,
            index_name=index,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )


# ---------------------------------------------------------------------------
# Database providers
# ---------------------------------------------------------------------------


class Supabase(_SupabaseBase):
    """Supabase database provider for chat history storage.

    Reads ``SUPABASE_URL`` and ``SUPABASE_KEY`` from the environment automatically.

    Args:
        url: Supabase project URL — overrides ``SUPABASE_URL``.
        key: Supabase API key — overrides ``SUPABASE_KEY``
             (also checks ``SUPABASE_SERVICE_ROLE_KEY``).

    Examples::

        Supabase()                         # reads from environment
        Supabase(url="https://x.supabase.co", key="...")
    """

    def __init__(
        self,
        url: str | None = None,
        key: str | None = None,
    ):
        if not url:
            url = os.getenv("SUPABASE_URL")
            if not url:
                raise ValueError(
                    "Supabase URL not found. "
                    "Set the SUPABASE_URL environment variable or pass url='https://...'."
                )

        if not key:
            key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if not key:
                raise ValueError(
                    "Supabase key not found. "
                    "Set the SUPABASE_KEY environment variable or pass key='...'."
                )

        super().__init__(url=url, key=key)


__all__ = [
    # LLM providers
    "Anthropic",
    "Cohere",
    "Gemini",
    "Mistral",
    "Ollama",
    "OpenAI",
    # Vector DB
    "Pinecone",
    # Database
    "Supabase",
]
