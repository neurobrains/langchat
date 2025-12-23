#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Agent with Tools Example - Creating an agent with custom tools.

This example demonstrates:
1. Defining custom tools
2. Creating an agent with tool support
3. Running agent with tool execution
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from langchat import Agent, Tool
from langchat.providers import OpenAIProvider

# Load environment variables
load_dotenv()


# Define custom tools
def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def search_web(query: str) -> str:
    """Search the web (mock implementation)."""
    # In a real implementation, you would use a search API
    return f"Mock search results for: {query}\n- Result 1: Information about {query}\n- Result 2: More details on {query}"


def get_weather(location: str) -> str:
    """Get weather information (mock implementation)."""
    # In a real implementation, you would use a weather API
    return f"Weather in {location}: Sunny, 22°C"


async def main():
    print("🛠️ LangChat Agent with Tools Example\n")

    # Create tools
    tools = [
        Tool(
            name="get_time",
            func=get_current_time,
            description="Get the current date and time"
        ),
        Tool(
            name="calculate",
            func=calculate,
            description="Calculate mathematical expressions like '25 * 17 + 100'"
        ),
        Tool(
            name="search",
            func=search_web,
            description="Search the web for information"
        ),
        Tool(
            name="weather",
            func=get_weather,
            description="Get weather information for a location"
        ),
    ]

    # Initialize agent with tools
    print("Initializing agent with tools...")
    agent = Agent(
        llm=OpenAIProvider(
            api_keys=[os.getenv("OPENAI_API_KEY")],
            model="gpt-4o-mini",
            temperature=0.7
        ),
        tools=tools,
        system_prompt="""You are a helpful assistant with access to various tools.
When you need to use a tool, use this format:
TOOL: tool_name
ARGS: argument

Available tools:
- get_time: Get current time (no arguments)
- calculate: Calculate math (argument: expression)
- search: Search web (argument: query)
- weather: Get weather (argument: location)

Use tools when appropriate and provide helpful responses.""",
        max_iterations=5,
        verbose=True
    )
    print(f"✅ Agent initialized with {len(tools)} tools\n")

    # Test queries
    print("Running agent tasks...")
    print("-" * 60)

    queries = [
        "What time is it right now?",
        "Calculate 123 * 456 + 789",
        "Search for information about machine learning",
        "What's the weather like in London?",
    ]

    for query in queries:
        print(f"\n👤 Query: {query}")
        response = await agent.run(query)
        print(f"🤖 Response: {response}")
        print("-" * 60)

    print("\n✅ All tasks completed!")


if __name__ == "__main__":
    asyncio.run(main())

