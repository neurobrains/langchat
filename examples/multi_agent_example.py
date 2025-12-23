#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Multi-Agent System Example - Coordinating multiple specialized agents.

This example demonstrates:
1. Creating specialized agents
2. Setting up a multi-agent system
3. Running workflows with agent coordination
"""

import asyncio
import os
from dotenv import load_dotenv

from langchat import Agent, MultiAgentSystem
from langchat.providers import OpenAIProvider

# Load environment variables
load_dotenv()


async def main():
    print("🤝 LangChat Multi-Agent System Example\n")

    # Create LLM provider
    llm_provider = OpenAIProvider(
        api_keys=[os.getenv("OPENAI_API_KEY")],
        model="gpt-4o-mini",
        temperature=0.7
    )

    # Create specialized agents
    print("Creating specialized agents...")
    
    researcher = Agent(
        llm=llm_provider,
        system_prompt="""You are a research specialist. Your role is to:
- Gather comprehensive information on topics
- Organize findings clearly
- Provide detailed research notes
Be thorough and factual.""",
        verbose=False
    )

    analyst = Agent(
        llm=llm_provider,
        system_prompt="""You are a data analyst. Your role is to:
- Analyze information and identify patterns
- Draw meaningful insights
- Highlight key findings
Be analytical and insightful.""",
        verbose=False
    )

    writer = Agent(
        llm=llm_provider,
        system_prompt="""You are a professional writer. Your role is to:
- Create clear, engaging content
- Structure information effectively
- Write in a professional tone
Be concise and well-structured.""",
        verbose=False
    )

    critic = Agent(
        llm=llm_provider,
        system_prompt="""You are a critical reviewer. Your role is to:
- Review content for accuracy and clarity
- Provide constructive feedback
- Suggest improvements
Be constructive and thorough.""",
        verbose=False
    )

    print("✅ Created 4 specialized agents\n")

    # Create multi-agent system
    print("Setting up multi-agent system...")
    system = MultiAgentSystem(verbose=True)
    system.add_agent("researcher", researcher)
    system.add_agent("analyst", analyst)
    system.add_agent("writer", writer)
    system.add_agent("critic", critic)
    print(f"✅ System initialized with agents: {system.list_agents()}\n")

    # Example 1: Sequential Workflow
    print("=" * 60)
    print("Example 1: Sequential Workflow")
    print("=" * 60)

    workflow = [
        ("researcher", "Research the current state of AI in healthcare"),
        ("analyst", "Analyze the research findings and identify key trends"),
        ("writer", "Write a clear summary of the analysis"),
        ("critic", "Review the summary and provide feedback"),
    ]

    print("\nExecuting workflow...")
    result = await system.run_workflow(workflow)
    
    print(f"\n📄 Final Output:\n{result['final_output']}")
    print("\n" + "=" * 60)

    # Example 2: Agent-to-Agent Communication
    print("\nExample 2: Agent-to-Agent Communication")
    print("=" * 60)

    print("\nSending message from researcher to analyst...")
    response = await system.send_message(
        from_agent="researcher",
        to_agent="analyst",
        content="I found that AI is being used in diagnostics, drug discovery, and patient monitoring. Can you analyze these applications?"
    )
    print(f"\n📩 Analyst Response:\n{response}")
    print("\n" + "=" * 60)

    # Example 3: Broadcast
    print("\nExample 3: Broadcasting to Multiple Agents")
    print("=" * 60)

    print("\nBroadcasting message to all agents...")
    responses = await system.broadcast(
        from_agent="coordinator",
        content="What is the most important aspect of AI ethics?",
        to_agents=["researcher", "analyst", "writer"]
    )

    for agent_name, response in responses.items():
        print(f"\n🤖 {agent_name.upper()}:\n{response}")

    print("\n" + "=" * 60)

    # Example 4: Round Robin
    print("\nExample 4: Round Robin Discussion")
    print("=" * 60)

    print("\nRunning round-robin discussion...")
    rr_result = await system.round_robin(
        task="What are the key challenges in AI safety?",
        rounds=2
    )

    print(f"\n📄 Final Consensus:\n{rr_result['final_output']}")
    print("\n" + "=" * 60)

    print("\n✅ Multi-agent examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

