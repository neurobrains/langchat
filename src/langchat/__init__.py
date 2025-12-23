# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LangChat - A powerful library for RAG, Agents, and Multi-Agent Systems.

Clean, linear imports:
  - from langchat import RAGAgent, Agent, MultiAgentSystem
  - from langchat.llm import OpenAI, Gemini, Anthropic, etc.
  - from langchat.vector_db import Pinecone
  - from langchat.database import Supabase
  - from langchat.reranker import Flashrank

Example:
    ```python
    from langchat import RAGAgent
    from langchat.llm import OpenAI
    from langchat.vector_db import Pinecone
    from langchat.database import Supabase
    from langchat.reranker import Flashrank

    # Initialize providers
    llm = OpenAI(api_keys=["sk-..."], model="gpt-4o-mini")
    vector_db = Pinecone(
        api_key="...",
        index_name="my-index",
        embedding_model="text-embedding-3-large",
        embedding_api_key="sk-..."
    )
    db = Supabase.from_config(supabase_url="...", supabase_key="...")
    reranker = Flashrank()

    # Create RAG agent
    agent = RAGAgent(llm=llm, vector_db=vector_db, db=db, reranker=reranker)

    # Chat
    response = await agent.chat("What is machine learning?", user_id="user123")
    print(response["response"])
    ```
"""

# Agent systems
from langchat.agents import Agent, AgentMessage, MultiAgentSystem, RAGAgent
from langchat.agents.agent import Tool

__version__ = "2.0.0"

__all__ = [
    # Agents
    "RAGAgent",
    "Agent",
    "Tool",
    "MultiAgentSystem",
    "AgentMessage",
]
