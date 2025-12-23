# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for LLM providers."""

import pytest

from langchat import LangChatConfig
from langchat.providers.llm import (
    AnthropicProvider,
    CohereProvider,
    GeminiProvider,
    MistralProvider,
    OllamaProvider,
    OpenAIProvider,
    create_llm_provider,
)


def test_openai_provider_creation():
    """Test OpenAI provider initialization."""
    provider = OpenAIProvider(
        api_keys=["test-key"],
        model="gpt-4o-mini",
        temperature=0.7
    )

    assert provider.model == "gpt-4o-mini"
    assert provider.temperature == 0.7
    assert provider.current_key == "test-key"


def test_openai_provider_requires_api_key():
    """Test that OpenAI provider requires API key."""
    with pytest.raises(ValueError, match="At least one OpenAI API key is required"):
        OpenAIProvider(api_keys=None)


def test_gemini_provider_creation():
    """Test Gemini provider initialization."""
    provider = GeminiProvider(
        api_keys=["test-key"],
        model="gemini-1.5-flash",
        temperature=1.0
    )

    assert provider.model == "gemini-1.5-flash"
    assert provider.temperature == 1.0


def test_anthropic_provider_creation():
    """Test Anthropic provider initialization."""
    provider = AnthropicProvider(
        api_keys=["test-key"],
        model="claude-3-5-sonnet-20241022",
        temperature=1.0
    )

    assert provider.model == "claude-3-5-sonnet-20241022"
    assert provider.temperature == 1.0


def test_ollama_provider_creation():
    """Test Ollama provider initialization."""
    provider = OllamaProvider(
        model="llama2",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    assert provider.model == "llama2"
    assert provider.temperature == 0.7


def test_cohere_provider_creation():
    """Test Cohere provider initialization."""
    provider = CohereProvider(
        api_keys=["test-key"],
        model="command",
        temperature=0.7
    )

    assert provider.model == "command"
    assert provider.temperature == 0.7


def test_mistral_provider_creation():
    """Test Mistral provider initialization."""
    provider = MistralProvider(
        api_keys=["test-key"],
        model="mistral-small-latest",
        temperature=0.7
    )

    assert provider.model == "mistral-small-latest"
    assert provider.temperature == 0.7


def test_create_llm_provider_openai():
    """Test factory with explicit OpenAI provider."""
    provider = create_llm_provider(
        "openai",
        api_keys=["test-key"],
        model="gpt-4"
    )

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-4"


def test_create_llm_provider_ollama():
    """Test factory with Ollama provider."""
    provider = create_llm_provider(
        "ollama",
        model="llama2",
        base_url="http://localhost:11434"
    )

    assert isinstance(provider, OllamaProvider)
    assert provider.model == "llama2"


def test_create_llm_provider_auto_with_config():
    """Test factory with auto and config."""
    config = LangChatConfig(
        openai_api_keys=["test-key"],
        openai_model="gpt-4o-mini"
    )

    provider = create_llm_provider("auto", config=config)
    assert isinstance(provider, OpenAIProvider)


def test_create_llm_provider_auto_no_keys():
    """Test factory auto-detection fails without keys."""
    config = LangChatConfig()

    with pytest.raises(ValueError, match="No API keys found"):
        create_llm_provider("auto", config=config)


def test_create_llm_provider_invalid():
    """Test factory with invalid provider name."""
    with pytest.raises(ValueError, match="Unknown provider"):
        create_llm_provider("invalid_provider")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

