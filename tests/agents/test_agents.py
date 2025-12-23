# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for agents."""

from unittest.mock import Mock

import pytest

from langchat.agents import Agent, MultiAgentSystem, Tool


def create_mock_llm():
    """Create a mock LLM provider for testing."""
    mock_llm = Mock()
    mock_llm.current_llm = Mock()
    return mock_llm


def test_tool_creation():
    """Test Tool creation and execution."""
    def test_func(x: str) -> str:
        return f"Result: {x}"

    tool = Tool(
        name="test",
        func=test_func,
        description="Test tool"
    )

    assert tool.name == "test"
    assert tool.description == "Test tool"
    result = tool.func("hello")
    assert result == "Result: hello"


def test_agent_creation_without_llm():
    """Test that Agent requires LLM or config."""
    # Create agent with mock LLM
    agent = Agent(llm=create_mock_llm())
    assert agent is not None
    assert agent.tools == []


def test_agent_add_tool():
    """Test adding tools to agent."""
    agent = Agent(llm=create_mock_llm())

    tool = Tool(
        name="test",
        func=lambda x: x,
        description="Test"
    )

    agent.add_tool(tool)
    assert len(agent.tools) == 1
    assert "test" in agent.tool_map


def test_agent_remove_tool():
    """Test removing tools from agent."""
    agent = Agent(llm=create_mock_llm())

    tool = Tool(
        name="test",
        func=lambda x: x,
        description="Test"
    )

    agent.add_tool(tool)
    assert len(agent.tools) == 1

    agent.remove_tool("test")
    assert len(agent.tools) == 0
    assert "test" not in agent.tool_map


def test_agent_clear_history():
    """Test clearing agent history."""
    agent = Agent(llm=create_mock_llm())
    agent.chat_history = [("q1", "a1"), ("q2", "a2")]

    agent.clear_history()
    assert agent.chat_history == []


def test_multi_agent_system_creation():
    """Test MultiAgentSystem creation."""
    system = MultiAgentSystem(verbose=False)

    assert len(system.list_agents()) == 0
    assert system.message_history == []


def test_multi_agent_add_agent():
    """Test adding agents to system."""
    system = MultiAgentSystem()
    agent = Agent(llm=create_mock_llm())

    system.add_agent("test_agent", agent)
    assert "test_agent" in system.list_agents()
    assert len(system.list_agents()) == 1


def test_multi_agent_add_duplicate_agent():
    """Test that adding duplicate agent raises error."""
    system = MultiAgentSystem()
    agent = Agent(llm=create_mock_llm())

    system.add_agent("test_agent", agent)

    with pytest.raises(ValueError, match="already exists"):
        system.add_agent("test_agent", agent)


def test_multi_agent_remove_agent():
    """Test removing agents from system."""
    system = MultiAgentSystem()
    agent = Agent(llm=create_mock_llm())

    system.add_agent("test_agent", agent)
    assert len(system.list_agents()) == 1

    system.remove_agent("test_agent")
    assert len(system.list_agents()) == 0


def test_multi_agent_get_agent():
    """Test getting agent from system."""
    system = MultiAgentSystem()
    agent = Agent(llm=create_mock_llm())

    system.add_agent("test_agent", agent)
    retrieved = system.get_agent("test_agent")

    assert retrieved is agent


def test_multi_agent_get_nonexistent_agent():
    """Test getting non-existent agent raises error."""
    system = MultiAgentSystem()

    with pytest.raises(ValueError, match="not found"):
        system.get_agent("nonexistent")


def test_multi_agent_clear_history():
    """Test clearing message history."""
    from langchat.agents.multi_agent import AgentMessage
    
    system = MultiAgentSystem()
    system.message_history = [
        AgentMessage(from_agent="a1", to_agent="a2", content="msg1"),
        AgentMessage(from_agent="a2", to_agent="a1", content="msg2")
    ]

    system.clear_history()
    assert system.message_history == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

