# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LangChat Providers - Modular providers for LLMs, Vector DBs, Databases, and more.
"""

from langchat.providers.database import Supabase, SupabaseProvider, create_database_provider

# LLM providers - import individually to avoid circular imports
from langchat.providers.llm.anthropic_provider import Anthropic, AnthropicProvider
from langchat.providers.llm.cohere_provider import Cohere, CohereProvider
from langchat.providers.llm.factory import create_llm_provider
from langchat.providers.llm.gemini_provider import Gemini, GeminiProvider
from langchat.providers.llm.mistral_provider import Mistral, MistralProvider
from langchat.providers.llm.ollama_provider import Ollama, OllamaProvider
from langchat.providers.llm.openai_provider import OpenAI, OpenAIProvider
from langchat.providers.reranker import Flashrank, FlashrankProvider, create_reranker_provider
from langchat.providers.vector_db import Pinecone, PineconeProvider, create_vector_db_provider

__all__ = [
    # LLM Providers (new names - recommended)
    "OpenAI",
    "Gemini",
    "Anthropic",
    "Ollama",
    "Cohere",
    "Mistral",
    "create_llm_provider",
    # LLM Providers (old names - backward compatibility)
    "OpenAIProvider",
    "GeminiProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "CohereProvider",
    "MistralProvider",
    # Vector DB Providers (new names - recommended)
    "Pinecone",
    "create_vector_db_provider",
    # Vector DB Providers (old names - backward compatibility)
    "PineconeProvider",
    # Database Providers (new names - recommended)
    "Supabase",
    "create_database_provider",
    # Database Providers (old names - backward compatibility)
    "SupabaseProvider",
    # Reranker Providers (new names - recommended)
    "Flashrank",
    "create_reranker_provider",
    # Reranker Providers (old names - backward compatibility)
    "FlashrankProvider",
]

