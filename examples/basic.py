#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Basic example — customer support chatbot.

A company indexes its support documentation once, then answers customer
questions in real time while keeping per-user conversation history.

Setup
-----
Create a .env file with:

    OPENAI_API_KEY=sk-...
    PINECONE_API_KEY=pc-...
    PINECONE_INDEX_NAME=support-docs
    SUPABASE_URL=https://yourproject.supabase.co
    SUPABASE_KEY=your-service-role-key

Run
---
    python examples/basic.py
"""

import asyncio

from langchat import LangChat
from langchat.providers import OpenAI, Pinecone, Supabase

# ---------------------------------------------------------------------------
# Build the assistant
# ---------------------------------------------------------------------------

lc = LangChat(
    llm=OpenAI("gpt-4o-mini"),  # reads OPENAI_API_KEY from env
    vector_db=Pinecone("support-docs"),  # reads PINECONE_API_KEY + OPENAI_API_KEY
    db=Supabase(),  # reads SUPABASE_URL + SUPABASE_KEY
)


# ---------------------------------------------------------------------------
# (One-time) index your support documents
# ---------------------------------------------------------------------------


def index_docs():
    """Run once to populate the vector store. Safe to call again — duplicates are skipped."""
    result = lc.index(
        ["docs/faq.pdf", "docs/returns-policy.pdf", "docs/shipping-guide.pdf"],
        chunk_size=800,
        chunk_overlap=100,
    )
    print(f"Indexed  : {result.get('total_chunks_indexed', 0)} chunks")
    print(f"Skipped  : {result.get('total_chunks_skipped', 0)} duplicates")


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


async def chat_session(user_id: str):
    """Simulate a multi-turn support conversation."""
    questions = [
        "How long does standard shipping take?",
        "Can I return a product after 30 days?",
        "Do you ship internationally?",
    ]

    print(f"\n=== Support session for {user_id} ===\n")

    for question in questions:
        print(f"Customer : {question}")

        response = await lc.chat(question, user_id=user_id, platform="support")

        if response:
            print(f"Assistant: {response.text}")
            print(f"          ({response.response_time:.2f}s)\n")
        else:
            print(f"Error    : {response.error}\n")


async def main():
    # index_docs()  # uncomment on first run

    # Simulate two independent users — each has isolated history
    await chat_session("customer-001")
    await chat_session("customer-002")


if __name__ == "__main__":
    asyncio.run(main())
