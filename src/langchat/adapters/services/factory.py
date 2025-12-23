# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING

from langchat.adapters.services.anthropic_service import AnthropicLLMService
from langchat.adapters.services.gemini_service import GeminiLLMService
from langchat.adapters.services.openai_service import OpenAILLMService

if TYPE_CHECKING:
    from langchat.config import LangChatConfig


def create_llm_service(config: LangChatConfig):
    """
    Create an LLM provider based on config.

    Provider resolution:
    - If `llm_provider` is explicit: use it.
    - If `auto`: prefer OpenAI, then Gemini, then Anthropic (based on keys present).
    """

    provider = (config.llm_provider or "auto").strip().lower()

    if provider == "auto":
        if config.openai_api_keys:
            provider = "openai"
        elif config.gemini_api_keys:
            provider = "gemini"
        elif config.anthropic_api_keys:
            provider = "anthropic"
        else:
            raise ValueError(
                "No API keys found for any provider. Set OPENAI_API_KEY(S), GEMINI_API_KEY(S)/GOOGLE_API_KEY, or ANTHROPIC_API_KEY(S)."
            )

    if provider == "openai":
        return OpenAILLMService(
            model=config.openai_model,
            temperature=config.openai_temperature,
            api_keys=config.openai_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    if provider == "gemini":
        return GeminiLLMService(
            model=config.gemini_model,
            temperature=config.gemini_temperature,
            api_keys=config.gemini_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    if provider == "anthropic":
        return AnthropicLLMService(
            model=config.anthropic_model,
            temperature=config.anthropic_temperature,
            api_keys=config.anthropic_api_keys,
            max_retries_per_key=config.max_llm_retries,
        )

    raise ValueError(f"Unknown llm_provider: {config.llm_provider!r} (expected auto/openai/gemini/anthropic)")


__all__ = ["create_llm_service"]


