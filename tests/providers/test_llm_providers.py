# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for LLM providers."""

import pytest

from langchat.llm import (
    Anthropic,
    Cohere,
    Gemini,
    Mistral,
    Ollama,
    OpenAI,
)


def test_openai_provider_creation():
    """Test OpenAI provider initialization."""
    provider = OpenAI(
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
        OpenAI(api_keys=None)


def test_gemini_provider_creation():
    """Test Gemini provider initialization."""
    provider = Gemini(
        api_keys=["test-key"],
        model="gemini-1.5-flash",
        temperature=1.0
    )

    assert provider.model == "gemini-1.5-flash"
    assert provider.temperature == 1.0


def test_anthropic_provider_creation():
    """Test Anthropic provider initialization."""
    provider = Anthropic(
        api_keys=["test-key"],
        model="claude-3-5-sonnet-20241022",
        temperature=1.0
    )

    assert provider.model == "claude-3-5-sonnet-20241022"
    assert provider.temperature == 1.0


def test_ollama_provider_creation():
    """Test Ollama provider initialization."""
    provider = Ollama(
        model="llama2",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    assert provider.model == "llama2"
    assert provider.temperature == 0.7


def test_cohere_provider_creation():
    """Test Cohere provider initialization."""
    provider = Cohere(
        api_keys=["test-key"],
        model="command",
        temperature=0.7
    )

    assert provider.model == "command"
    assert provider.temperature == 0.7


def test_mistral_provider_creation():
    """Test Mistral provider initialization."""
    provider = Mistral(
        api_keys=["test-key"],
        model="mistral-small-latest",
        temperature=0.7
    )

    assert provider.model == "mistral-small-latest"
    assert provider.temperature == 0.7




if __name__ == "__main__":
    pytest.main([__file__, "-v"])

