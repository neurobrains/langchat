# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LangChat — a production-ready RAG chat framework.

Quick start::

    from langchat import LangChat
    from langchat.providers import OpenAI, Pinecone, Supabase

    lc = LangChat(
        llm=OpenAI("gpt-4o"),
        vector_db=Pinecone("my-index"),
        db=Supabase(),
    )

    response = await lc.chat("What is RAG?", user_id="alice")
    print(response.text)

All providers read credentials from environment variables automatically:

    OPENAI_API_KEY      PINECONE_API_KEY      SUPABASE_URL / SUPABASE_KEY
    ANTHROPIC_API_KEY   GEMINI_API_KEY        MISTRAL_API_KEY   COHERE_API_KEY
"""

from langchat.sdk import LangChat
from langchat.types import ChatResponse

__version__ = "1.0.2"

__all__ = [
    "LangChat",
    "ChatResponse",
    "providers",
]


def __getattr__(name: str):
    # Lazy-load `providers` so that optional adapter dependencies
    # (supabase, pinecone, …) are only imported when actually needed.
    if name == "providers":
        import langchat.providers as _providers  # avoids recursive __getattr__ call

        return _providers
    raise AttributeError(f"module 'langchat' has no attribute {name!r}")
