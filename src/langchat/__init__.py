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
    AnthropicProvider,
    CohereProvider,
    # Reranker Providers
    FlashrankProvider,
    GeminiProvider,
    MistralProvider,
    OllamaProvider,
    # LLM Providers
    OpenAIProvider,
    # Vector DB Providers
    PineconeProvider,
    # Database Providers
    SupabaseProvider,
    create_database_provider,
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
    # LLM Providers
    "OpenAIProvider",
    "GeminiProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "CohereProvider",
    "MistralProvider",
    "create_llm_provider",
    # Vector DB Providers
    "PineconeProvider",
    "create_vector_db_provider",
    # Database Providers
    "SupabaseProvider",
    "create_database_provider",
    # Reranker Providers
    "FlashrankProvider",
    "create_reranker_provider",
]


