# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LLM Module - Support for multiple LLM providers.
"""

from langchat.llm.anthropic_provider import Anthropic, AnthropicProvider
from langchat.llm.cohere_provider import Cohere, CohereProvider
from langchat.llm.gemini_provider import Gemini, GeminiProvider
from langchat.llm.mistral_provider import Mistral, MistralProvider
from langchat.llm.ollama_provider import Ollama, OllamaProvider
from langchat.llm.openai_provider import OpenAI, OpenAIProvider

__all__ = [
    # New names (recommended)
    "OpenAI",
    "Gemini",
    "Anthropic",
    "Ollama",
    "Cohere",
    "Mistral",
    # Old names (backward compatibility)
    "OpenAIProvider",
    "GeminiProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "CohereProvider",
    "MistralProvider",
]
