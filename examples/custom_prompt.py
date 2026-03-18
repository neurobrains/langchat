#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Custom prompt example — internal HR knowledge base.

An HR bot that answers employee questions using the company handbook.
Uses a custom system prompt to enforce tone and citation rules.

Setup
-----
    OPENAI_API_KEY=sk-...
    PINECONE_API_KEY=pc-...
    PINECONE_INDEX_NAME=hr-handbook
    SUPABASE_URL=https://yourproject.supabase.co
    SUPABASE_KEY=your-service-role-key

Run
---
    python examples/custom_prompt.py
"""

import asyncio

from langchat import LangChat
from langchat.providers import OpenAI, Pinecone, Supabase

# ---------------------------------------------------------------------------
# Prompt — controls tone and rules
# ---------------------------------------------------------------------------

HR_PROMPT = """You are Aria, an HR assistant for Acme Corp.

Rules:
- Answer ONLY from the provided context. Never guess.
- Be concise, professional, and friendly.
- If the answer is not in the context, say: "I don't have that information.
  Please contact HR at hr@acme.com."
- Always end with: "Is there anything else I can help you with?"

Context:
{context}

Conversation so far:
{chat_history}

Employee question: {question}
Aria:"""

# ---------------------------------------------------------------------------
# Build the assistant
# ---------------------------------------------------------------------------

lc = LangChat(
    llm=OpenAI("gpt-4o", temperature=0.3),  # lower temperature = more focused answers
    vector_db=Pinecone("hr-handbook"),
    db=Supabase(),
    prompt_template=HR_PROMPT,
    max_chat_history=10,  # keep last 10 exchanges in context
)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


async def hr_chat(employee_id: str):
    questions = [
        "How many days of annual leave do I get?",
        "What is the parental leave policy?",
        "How do I submit an expense claim?",
        "Can I work remotely full-time?",
    ]

    print(f"\n=== HR session for employee {employee_id} ===\n")

    for q in questions:
        print(f"Employee : {q}")

        response = await lc.chat(q, user_id=employee_id, platform="hr")

        if response:
            print(f"Aria     : {response.text}\n")
        else:
            print(f"[Error]  : {response.error}\n")


async def main():
    await hr_chat("emp-1042")


if __name__ == "__main__":
    asyncio.run(main())
