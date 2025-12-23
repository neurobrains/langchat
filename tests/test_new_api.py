# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for the new LangChat 2.0 API."""

import pytest

from langchat import (
    Agent,
    LangChatConfig,
    MultiAgentSystem,
    RAGAgent,
    Tool,
)
from langchat.providers import (
    create_llm_provider,
)


def test_imports():
    """Test that all new API components can be imported."""
    assert RAGAgent is not None
    assert Agent is not None
    assert MultiAgentSystem is not None
    assert Tool is not None
    assert LangChatConfig is not None


def test_config_creation():
    """Test config creation with explicit values."""
    config = LangChatConfig(
        openai_api_keys=["test-key"],
        openai_model="gpt-4o-mini",
        pinecone_api_key="test-pinecone-key",
        pinecone_index_name="test-index",
        supabase_url="https://test.supabase.co",
        supabase_key="test-supabase-key",
    )

    assert config.openai_api_keys == ["test-key"]
    assert config.openai_model == "gpt-4o-mini"
    assert config.pinecone_api_key == "test-pinecone-key"


def test_tool_creation():
    """Test Tool creation."""
    def test_func(x: str) -> str:
        return f"Result: {x}"

    tool = Tool(
        name="test_tool",
        func=test_func,
        description="A test tool"
    )

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.func("hello") == "Result: hello"


def test_multi_agent_system_creation():
    """Test MultiAgentSystem creation and basic operations."""
    system = MultiAgentSystem(verbose=False)

    assert len(system.list_agents()) == 0
    assert system.message_history == []


def test_llm_provider_factory_invalid():
    """Test that invalid provider raises error."""
    with pytest.raises(ValueError, match="Unknown provider"):
        create_llm_provider("invalid_provider")


def test_config_with_new_providers():
    """Test config supports new providers."""
    config = LangChatConfig(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama2",
        cohere_api_keys=["test-cohere-key"],
        cohere_model="command",
        mistral_api_keys=["test-mistral-key"],
        mistral_model="mistral-small-latest",
    )

    assert config.ollama_base_url == "http://localhost:11434"
    assert config.ollama_model == "llama2"
    assert config.cohere_api_keys == ["test-cohere-key"]
    assert config.mistral_api_keys == ["test-mistral-key"]


def test_version():
    """Test that version is set."""
    import langchat
    assert hasattr(langchat, "__version__")
    assert langchat.__version__ == "2.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

