# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Single Agent - General purpose agent with tools support."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from langchat.adapters.logger import logger


class Tool:
    """
    Tool definition for agents.

    A tool is a function that the agent can call to perform actions.
    """

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict[str, Any] | None = None,
    ):
        """
        Initialize a tool.

        Args:
            name: Tool name
            func: Function to execute
            description: Description of what the tool does
            parameters: Parameter schema for the tool
        """
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters or {}

    async def run(self, *args, **kwargs) -> Any:
        """Run the tool."""
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Tool(name='{self.name}', description='{self.description}')"


class Agent:
    """
    General purpose Agent with tools support.

    Can be used for task automation, function calling, and reasoning.

    Example:
        ```python
        from langchat import Agent
        from langchat.providers import OpenAIProvider

        # Define tools
        def search_web(query: str) -> str:
            # Your search implementation
            return f"Search results for: {query}"

        def calculate(expression: str) -> float:
            return eval(expression)

        # Create agent
        agent = Agent(
            llm=OpenAIProvider(api_keys=["sk-..."], model="gpt-4"),
            tools=[
                Tool(name="search", func=search_web, description="Search the web"),
                Tool(name="calc", func=calculate, description="Calculate math expressions")
            ],
            system_prompt="You are a helpful assistant with access to tools."
        )

        # Run agent
        response = await agent.run("What is 25 * 17?")
        print(response)
        ```
    """

    def __init__(
        self,
        llm: Any = None,
        tools: list[Tool] | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 5,
        verbose: bool = False,
    ):
        """
        Initialize Agent.

        Args:
            llm: LLM provider instance (required)
            tools: List of Tool instances
            system_prompt: System prompt for the agent
            max_iterations: Maximum reasoning iterations
            verbose: Enable verbose logging
        """
        if llm is None:
            raise ValueError(
                "LLM provider is required. Please provide an LLM instance:\n"
                "Example: Agent(llm=OpenAI(api_keys=['sk-...'], model='gpt-4o-mini'))"
            )
        self.llm = llm
        self.tools = tools or []
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.chat_history: list[tuple[str, str]] = []

        logger.info(f"Agent initialized with {len(self.tools)} tools")

    def _default_system_prompt(self) -> str:
        """Generate default system prompt."""
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in self.tools
        )

        return f"""You are a helpful AI assistant with access to tools.

Available tools:
{tool_descriptions if tool_descriptions else "No tools available"}

When you need to use a tool, respond in this format:
TOOL: tool_name
ARGS: argument1, argument2, ...

When you have the final answer, respond normally without using the TOOL format.
"""

    async def run(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Run the agent on a query.

        Args:
            query: User query
            context: Additional context for the agent

        Returns:
            Agent's response
        """
        try:
            iteration = 0
            current_query = query
            tool_outputs = []

            while iteration < self.max_iterations:
                iteration += 1

                # Build prompt
                prompt = self._build_prompt(current_query, tool_outputs, context)

                # Get LLM response
                from langchain_core.messages import HumanMessage
                response = await self.llm.current_llm.ainvoke([HumanMessage(content=prompt)])
                response_text = response.content if hasattr(response, "content") else str(response)

                if self.verbose:
                    logger.info(f"Iteration {iteration}: {response_text}")

                # Check if tool use is requested
                if "TOOL:" in response_text and "ARGS:" in response_text:
                    tool_name, args = self._parse_tool_call(response_text)

                    if tool_name in self.tool_map:
                        # Execute tool
                        try:
                            tool_output = await self.tool_map[tool_name].run(*args)
                            tool_outputs.append({
                                "tool": tool_name,
                                "args": args,
                                "output": tool_output
                            })

                            if self.verbose:
                                logger.info(f"Tool {tool_name} output: {tool_output}")

                            # Continue with tool output
                            current_query = f"Tool output: {tool_output}\nContinue reasoning."
                            continue
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {e}")
                            return f"Error executing tool: {str(e)}"
                    else:
                        return f"Unknown tool: {tool_name}"
                else:
                    # Final answer
                    self.chat_history.append((query, response_text))
                    return response_text

            return "Max iterations reached without final answer."

        except Exception as e:
            logger.error(f"Error in agent run: {e}")
            return f"Error: {str(e)}"

    def run_sync(self, query: str, context: dict[str, Any] | None = None) -> str:
        """
        Synchronous version of run method.

        Args:
            query: User query
            context: Additional context

        Returns:
            Agent's response
        """
        return asyncio.run(self.run(query, context))

    def _build_prompt(
        self,
        query: str,
        tool_outputs: list[dict[str, Any]],
        context: dict[str, Any] | None,
    ) -> str:
        """Build prompt for the agent."""
        parts = [self.system_prompt, ""]

        if context:
            parts.append(f"Context: {context}")
            parts.append("")

        if tool_outputs:
            parts.append("Previous tool executions:")
            for output in tool_outputs:
                parts.append(f"- {output['tool']}{output['args']}: {output['output']}")
            parts.append("")

        if self.chat_history:
            parts.append("Chat History:")
            for q, a in self.chat_history[-3:]:  # Last 3 exchanges
                parts.append(f"User: {q}")
                parts.append(f"Assistant: {a}")
            parts.append("")

        parts.append(f"User Query: {query}")

        return "\n".join(parts)

    def _parse_tool_call(self, response: str) -> tuple[str, list[str]]:
        """Parse tool call from response."""
        lines = response.split("\n")
        tool_name = ""
        args = []

        for line in lines:
            if line.startswith("TOOL:"):
                tool_name = line.replace("TOOL:", "").strip()
            elif line.startswith("ARGS:"):
                args_str = line.replace("ARGS:", "").strip()
                args = [arg.strip() for arg in args_str.split(",") if arg.strip()]

        return tool_name, args

    def add_tool(self, tool: Tool):
        """Add a tool to the agent."""
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        logger.info(f"Tool '{tool.name}' added to agent")

    def remove_tool(self, tool_name: str):
        """Remove a tool from the agent."""
        if tool_name in self.tool_map:
            tool = self.tool_map[tool_name]
            self.tools.remove(tool)
            del self.tool_map[tool_name]
            logger.info(f"Tool '{tool_name}' removed from agent")

    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []


__all__ = ["Agent", "Tool"]

