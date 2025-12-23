# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for the new LangChat 2.0 API."""

import pytest

from langchat import (
    Agent,
    MultiAgentSystem,
    RAGAgent,
    Tool,
)


def test_imports():
    """Test that all new API components can be imported."""
    assert RAGAgent is not None
    assert Agent is not None
    assert MultiAgentSystem is not None
    assert Tool is not None


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




def test_version():
    """Test that version is set."""
    import langchat
    assert hasattr(langchat, "__version__")
    assert langchat.__version__ == "2.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

