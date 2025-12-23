# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING

from langchat.adapters.services.anthropic_service import AnthropicLLMService
from langchat.adapters.services.gemini_service import GeminiLLMService
from langchat.adapters.services.openai_service import OpenAILLMService

if TYPE_CHECKING:
    from langchat.adapters.base import LLMProvider
    from langchat.config import LangChatConfig


def _auto_provider(config: LangChatConfig) -> str:
    if config.openai_api_keys:
        return "openai"
    if config.gemini_api_keys:
        return "gemini"
    if config.anthropic_api_keys:
        return "anthropic"
    return "openai"


def create_llm_service(config: LangChatConfig) -> LLMProvider:
    """
    Create an LLMProvider based on config.llm_provider.

    If llm_provider is "auto", choose based on which keys are present.
    """
    provider = (config.llm_provider or "auto").strip().lower()
    if provider == "auto":
        provider = _auto_provider(config)

    if provider == "openai":
        if not config.openai_api_keys:
            raise ValueError("OpenAI API keys must be provided (OPENAI_API_KEY / OPENAI_API_KEYS)")
        return OpenAILLMService(
            model=config.openai_model,
            temperature=config.openai_temperature,
            api_keys=config.openai_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    if provider == "gemini":
        if not config.gemini_api_keys:
            raise ValueError("Gemini API key must be provided (GEMINI_API_KEY / GOOGLE_API_KEY)")
        return GeminiLLMService(
            model=config.gemini_model,
            temperature=config.gemini_temperature,
            api_keys=config.gemini_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    if provider == "anthropic":
        if not config.anthropic_api_keys:
            raise ValueError("Anthropic API key must be provided (ANTHROPIC_API_KEY / ANTHROPIC_API_KEYS)")
        return AnthropicLLMService(
            model=config.anthropic_model,
            temperature=config.anthropic_temperature,
            api_keys=config.anthropic_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    raise ValueError(f"Unknown llm_provider: {config.llm_provider!r} (expected auto/openai/gemini/anthropic)")


