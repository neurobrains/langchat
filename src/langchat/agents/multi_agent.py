# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Multi-Agent System - Orchestrate communication between multiple agents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langchat.adapters.logger import logger

if TYPE_CHECKING:
    from langchat.agents.agent import Agent


@dataclass
class AgentMessage:
    """Message passed between agents."""

    from_agent: str
    to_agent: str
    content: str
    metadata: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return f"Message({self.from_agent} -> {self.to_agent}: {self.content[:50]}...)"


class MultiAgentSystem:
    """
    Multi-Agent System for agent-to-agent communication.

    Allows multiple agents to work together on complex tasks by
    communicating and coordinating their actions.

    Example:
        ```python
        from langchat import Agent, MultiAgentSystem
        from langchat.providers import OpenAIProvider

        # Create specialized agents
        researcher = Agent(
            llm=OpenAIProvider(api_keys=["sk-..."], model="gpt-4"),
            system_prompt="You are a research specialist. Gather information.",
            tools=[search_tool]
        )

        analyst = Agent(
            llm=OpenAIProvider(api_keys=["sk-..."], model="gpt-4"),
            system_prompt="You are an analyst. Analyze information and draw conclusions."
        )

        writer = Agent(
            llm=OpenAIProvider(api_keys=["sk-..."], model="gpt-4"),
            system_prompt="You are a writer. Create well-written summaries."
        )

        # Create multi-agent system
        system = MultiAgentSystem()
        system.add_agent("researcher", researcher)
        system.add_agent("analyst", analyst)
        system.add_agent("writer", writer)

        # Define workflow
        workflow = [
            ("researcher", "Find information about AI trends in 2024"),
            ("analyst", "Analyze the research findings"),
            ("writer", "Write a summary report")
        ]

        # Run the system
        result = await system.run_workflow(workflow)
        print(result)
        ```
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize Multi-Agent System.

        Args:
            verbose: Enable verbose logging
        """
        self.agents: dict[str, Agent] = {}
        self.message_history: list[AgentMessage] = []
        self.verbose = verbose

        logger.info("Multi-Agent System initialized")

    def add_agent(self, name: str, agent: Agent):
        """
        Add an agent to the system.

        Args:
            name: Unique name for the agent
            agent: Agent instance
        """
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")

        self.agents[name] = agent
        logger.info(f"Agent '{name}' added to system")

    def remove_agent(self, name: str):
        """
        Remove an agent from the system.

        Args:
            name: Agent name
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Agent '{name}' removed from system")

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Send a message from one agent to another.

        Args:
            from_agent: Sender agent name
            to_agent: Receiver agent name
            content: Message content
            metadata: Optional metadata

        Returns:
            Response from the receiving agent
        """
        if to_agent not in self.agents:
            raise ValueError(f"Agent '{to_agent}' not found")

        # Create message
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            metadata=metadata,
        )
        self.message_history.append(message)

        if self.verbose:
            logger.info(f"Message: {from_agent} -> {to_agent}")

        # Get agent's response
        context = {
            "from_agent": from_agent,
            "message_history": self.message_history[-5:],  # Last 5 messages
        }
        response = await self.agents[to_agent].run(content, context)

        return response

    async def run_workflow(
        self,
        workflow: list[tuple[str, str]],
        initial_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run a sequential workflow across agents.

        Args:
            workflow: List of (agent_name, task) tuples
            initial_context: Initial context for the workflow

        Returns:
            Dictionary with workflow results

        Example:
            ```python
            workflow = [
                ("researcher", "Research AI trends"),
                ("analyst", "Analyze findings"),
                ("writer", "Write summary")
            ]
            result = await system.run_workflow(workflow)
            ```
        """
        results = {}
        context = initial_context or {}
        previous_output = ""

        for i, (agent_name, task) in enumerate(workflow):
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not found in workflow")

            if self.verbose:
                logger.info(f"Step {i+1}: {agent_name} - {task}")

            # Build task with context
            full_task = task
            if previous_output:
                full_task = f"Previous step output: {previous_output}\n\nYour task: {task}"

            # Run agent
            output = await self.agents[agent_name].run(full_task, context)
            results[f"step_{i+1}_{agent_name}"] = output
            previous_output = output

            # Update context
            context[f"step_{i+1}"] = output

        return {
            "final_output": previous_output,
            "steps": results,
            "message_history": self.message_history,
        }

    def run_workflow_sync(
        self,
        workflow: list[tuple[str, str]],
        initial_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Synchronous version of run_workflow.

        Args:
            workflow: List of (agent_name, task) tuples
            initial_context: Initial context

        Returns:
            Dictionary with workflow results
        """
        return asyncio.run(self.run_workflow(workflow, initial_context))

    async def broadcast(
        self,
        from_agent: str,
        content: str,
        to_agents: list[str] | None = None,
    ) -> dict[str, str]:
        """
        Broadcast a message to multiple agents.

        Args:
            from_agent: Sender agent name
            content: Message content
            to_agents: List of receiver agent names (None = all agents)

        Returns:
            Dictionary mapping agent names to their responses
        """
        if to_agents is None:
            to_agents = [name for name in self.agents if name != from_agent]

        responses = {}
        for agent_name in to_agents:
            response = await self.send_message(from_agent, agent_name, content)
            responses[agent_name] = response

        return responses

    async def round_robin(
        self,
        task: str,
        rounds: int = 1,
    ) -> dict[str, Any]:
        """
        Execute a task in round-robin fashion across all agents.

        Each agent processes the task and passes it to the next agent.

        Args:
            task: Initial task
            rounds: Number of rounds

        Returns:
            Dictionary with round results
        """
        if not self.agents:
            raise ValueError("No agents in the system")

        agent_names = list(self.agents.keys())
        results = []
        current_task = task

        for round_num in range(rounds):
            round_results = {}

            for agent_name in agent_names:
                if self.verbose:
                    logger.info(f"Round {round_num + 1}, Agent: {agent_name}")

                response = await self.agents[agent_name].run(current_task)
                round_results[agent_name] = response
                current_task = response  # Next agent builds on previous output

            results.append(round_results)

        return {
            "rounds": results,
            "final_output": current_task,
        }

    def get_agent(self, name: str) -> Agent:
        """
        Get an agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance
        """
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found")
        return self.agents[name]

    def list_agents(self) -> list[str]:
        """Get list of agent names in the system."""
        return list(self.agents.keys())

    def clear_history(self):
        """Clear message history."""
        self.message_history = []
        logger.info("Message history cleared")


__all__ = ["MultiAgentSystem", "AgentMessage"]

