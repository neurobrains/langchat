#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Provider Comparison Example - Testing different LLM providers.

This example demonstrates:
1. Using multiple LLM providers
2. Comparing responses from different models
3. Switching providers easily
"""

import asyncio
import os
from dotenv import load_dotenv

from langchat import Agent
from langchat.providers import (
    OpenAIProvider,
    GeminiProvider,
    AnthropicProvider,
    OllamaProvider,
)

# Load environment variables
load_dotenv()


async def test_provider(provider_name: str, provider, query: str):
    """Test a provider with a query."""
    print(f"\n{'='*60}")
    print(f"Testing: {provider_name}")
    print(f"{'='*60}")
    
    try:
        agent = Agent(
            llm=provider,
            system_prompt="You are a helpful assistant. Provide concise, accurate answers.",
            verbose=False
        )
        
        response = await agent.run(query)
        print(f"\n✅ Response:\n{response}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


async def main():
    print("🔄 LangChat Provider Comparison Example\n")

    query = "Explain what RAG (Retrieval Augmented Generation) is in 2-3 sentences."
    
    print(f"Query: {query}\n")

    # Test OpenAI
    if os.getenv("OPENAI_API_KEY"):
        await test_provider(
            "OpenAI GPT-4o-mini",
            OpenAIProvider(
                api_keys=[os.getenv("OPENAI_API_KEY")],
                model="gpt-4o-mini",
                temperature=0.7
            ),
            query
        )

    # Test Gemini
    if os.getenv("GEMINI_API_KEY"):
        await test_provider(
            "Google Gemini 1.5 Flash",
            GeminiProvider(
                api_keys=[os.getenv("GEMINI_API_KEY")],
                model="gemini-1.5-flash",
                temperature=0.7
            ),
            query
        )

    # Test Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        await test_provider(
            "Anthropic Claude 3.5 Sonnet",
            AnthropicProvider(
                api_keys=[os.getenv("ANTHROPIC_API_KEY")],
                model="claude-3-5-sonnet-20241022",
                temperature=0.7
            ),
            query
        )

    # Test Ollama (local)
    try:
        await test_provider(
            "Ollama Llama2 (Local)",
            OllamaProvider(
                model="llama2",
                base_url="http://localhost:11434",
                temperature=0.7
            ),
            query
        )
    except Exception as e:
        print(f"\n⚠️ Ollama not available: {str(e)}")
        print("   Install Ollama and run 'ollama pull llama2' to test local models")

    print("\n" + "="*60)
    print("✅ Provider comparison complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

