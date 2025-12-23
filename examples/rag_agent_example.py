#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
RAG Agent Example - Building a knowledge base chatbot.

This example demonstrates:
1. Creating a RAG agent
2. Loading and indexing documents
3. Chatting with contextual responses
"""

import asyncio
import os
from dotenv import load_dotenv

from langchat import RAGAgent
from langchat.providers import OpenAIProvider, PineconeProvider, SupabaseProvider

# Load environment variables
load_dotenv()


async def main():
    print("🤖 LangChat RAG Agent Example\n")

    # Initialize RAG agent
    print("Initializing RAG agent...")
    agent = RAGAgent(
        llm=OpenAIProvider(
            api_keys=[os.getenv("OPENAI_API_KEY")],
            model="gpt-4o-mini",
            temperature=0.7
        ),
        vector_db=PineconeProvider(
            api_key=os.getenv("PINECONE_API_KEY"),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            embedding_model="text-embedding-3-large",
            embedding_api_key=os.getenv("OPENAI_API_KEY")
        ),
        db=SupabaseProvider.from_config(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        ),
        verbose=True
    )
    print("✅ RAG agent initialized\n")

    # Optional: Load documents (uncomment to index your documents)
    # print("Loading documents...")
    # result = agent.load_documents(
    #     "path/to/your/document.pdf",
    #     chunk_size=1000,
    #     chunk_overlap=200
    # )
    # print(f"✅ Indexed {result['chunks_indexed']} chunks\n")

    # Chat with the agent
    user_id = "demo_user"
    
    print("Starting conversation...")
    print("-" * 60)

    queries = [
        "Hello! What can you help me with?",
        "Tell me about artificial intelligence",
        "What are the key applications?",
    ]

    for query in queries:
        print(f"\n👤 User: {query}")
        
        response = await agent.chat(
            query=query,
            user_id=user_id,
            domain="demo",
            return_sources=True
        )
        
        print(f"🤖 Agent: {response['response']}")
        
        if "sources" in response:
            print(f"\n📚 Sources: {len(response['sources'])} documents used")

    print("\n" + "-" * 60)
    print("✅ Conversation complete!")


if __name__ == "__main__":
    asyncio.run(main())

