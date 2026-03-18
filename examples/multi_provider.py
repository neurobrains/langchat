#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Multi-provider example — swap LLMs without changing anything else.

Demonstrates how to use the same vector store and database with different
LLM providers: OpenAI, Anthropic, Gemini, Mistral, Cohere, and local Ollama.

Great for:
- A/B testing different models
- Fallback chains
- Cost optimisation (cheap model for simple queries, powerful for complex)

Setup
-----
Set whichever keys you have — unused providers are simply not instantiated:

    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...
    GEMINI_API_KEY=...
    MISTRAL_API_KEY=...
    COHERE_API_KEY=...
    PINECONE_API_KEY=pc-...
    PINECONE_INDEX_NAME=my-index
    SUPABASE_URL=https://yourproject.supabase.co
    SUPABASE_KEY=your-key

Run
---
    python examples/multi_provider.py
"""

import asyncio
import os

from langchat import LangChat
from langchat.providers import (
    Anthropic,
    Cohere,
    Gemini,
    Mistral,
    Ollama,
    OpenAI,
    Pinecone,
    Supabase,
)

QUERY = "What is retrieval-augmented generation and why does it matter?"
INDEX = os.getenv("PINECONE_INDEX_NAME", "my-index")


def _build(llm) -> LangChat:
    return LangChat(
        llm=llm,
        vector_db=Pinecone(INDEX),
        db=Supabase(),
    )


async def run_provider(name: str, lc: LangChat) -> None:
    response = await lc.chat(QUERY, user_id=f"demo-{name}", platform="ai-research")
    status = "✓" if response else "✗"
    print(f"\n[{name}] {status}  ({response.response_time:.2f}s)")
    print(f"  {response.text[:200]}{'...' if len(response.text) > 200 else ''}")


async def main():
    providers: list[tuple[str, LangChat]] = []

    # Add whichever providers you have keys for
    if os.getenv("OPENAI_API_KEY"):
        providers.append(("OpenAI gpt-4o-mini", _build(OpenAI("gpt-4o-mini"))))
        providers.append(("OpenAI gpt-4o", _build(OpenAI("gpt-4o"))))

    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append(("Anthropic Sonnet", _build(Anthropic("claude-3-5-sonnet-20241022"))))

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        providers.append(("Gemini Flash", _build(Gemini("gemini-1.5-flash"))))

    if os.getenv("MISTRAL_API_KEY"):
        providers.append(("Mistral Small", _build(Mistral("mistral-small-latest"))))

    if os.getenv("COHERE_API_KEY"):
        providers.append(("Cohere Command", _build(Cohere("command"))))

    # Ollama runs locally — no key required
    providers.append(("Ollama llama2 (local)", _build(Ollama("llama2"))))

    if not providers:
        print("No API keys found. Set at least one provider key in your .env file.")
        return

    print(f"Query: {QUERY}\n")
    print(f"Testing {len(providers)} provider(s)...\n{'─' * 60}")

    # Run all providers concurrently
    await asyncio.gather(*(run_provider(name, lc) for name, lc in providers))


if __name__ == "__main__":
    asyncio.run(main())
