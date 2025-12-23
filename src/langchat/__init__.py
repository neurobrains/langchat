# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LangChat - A powerful library for RAG, Agents, and Multi-Agent Systems.

Clean API for easy integration:
  - from langchat import RAGAgent, Agent, MultiAgentSystem
  - from langchat import LangChat, LangChatConfig  # Legacy API (still supported)
  - from langchat.providers import OpenAIProvider, GeminiProvider, etc.
"""

# Core configuration
# New Agent-based API
from langchat.agents import Agent, AgentMessage, MultiAgentSystem, RAGAgent
from langchat.agents.agent import Tool
from langchat.core.config import LangChatConfig

# Providers (for easy access)
from langchat.providers import (
    Anthropic,
    AnthropicProvider,
    Cohere,
    CohereProvider,
    # Reranker Providers
    Flashrank,
    FlashrankProvider,
    Gemini,
    GeminiProvider,
    Mistral,
    MistralProvider,
    Ollama,
    OllamaProvider,
    # LLM Providers (new names)
    OpenAI,
    # LLM Providers (old names - backward compatibility)
    OpenAIProvider,
    # Vector DB Providers
    Pinecone,
    PineconeProvider,
    # Database Providers
    Supabase,
    SupabaseProvider,
    create_database_provider,
    # Factory functions
    create_llm_provider,
    create_reranker_provider,
    create_vector_db_provider,
)

# Legacy SDK (backward compatibility)
from langchat.sdk import LangChat

__version__ = "2.0.0"

__all__ = [
    # Configuration
    "LangChatConfig",
    # Legacy SDK
    "LangChat",
    # Agents
    "RAGAgent",
    "Agent",
    "Tool",
    "MultiAgentSystem",
    "AgentMessage",
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
    # Vector DB Providers
    "Pinecone",
    "PineconeProvider",
    "create_vector_db_provider",
    # Database Providers
    "Supabase",
    "SupabaseProvider",
    "create_database_provider",
    # Reranker Providers
    "Flashrank",
    "FlashrankProvider",
    "create_reranker_provider",
]


