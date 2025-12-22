# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import asyncio
import os
from typing import List

from langchat import LangChat, LangChatConfig

# ============================================================================
# Custom Prompts for Education Domain
# ============================================================================

EDUCATION_SYSTEM_PROMPT = """You are an expert educational assistant specializing in helping students learn effectively.

Your expertise includes:
- Explaining complex concepts in simple, understandable terms
- Providing step-by-step solutions to problems
- Offering study tips and learning strategies
- Answering questions about various subjects (math, science, history, literature, etc.)
- Helping with homework and assignments
- Providing educational resources and recommendations

Be patient, encouraging, and clear. Break down complex topics into digestible parts.
Always encourage critical thinking and provide examples when helpful.

Use the following context from educational materials to answer questions:
{context}

Previous conversation: {chat_history}

Student's question: {question}
Your response:"""

EDUCATION_STANDALONE_PROMPT = """Convert this educational question to a standalone search query that would help find relevant educational content.

Make sure the query captures the learning intent and key concepts.

Previous conversation: {chat_history}
Current question: {question}
Standalone educational query:"""


# ============================================================================
# Example Usage with Default Providers
# ============================================================================

async def example_basic_usage():
    """
    Basic example using default providers (OpenAI, Pinecone, Supabase, FlashRank).
    
    This demonstrates the standard usage pattern. The adapter pattern is working
    behind the scenes - all providers are abstracted through interfaces.
    """
    
    # Option 1: Load from environment variables
    # Set these in your .env file or environment:
    # OPENAI_API_KEYS=sk-...
    # PINECONE_API_KEY=pcsk-...
    # PINECONE_INDEX_NAME=your-index
    # SUPABASE_URL=https://xxxxx.supabase.co
    # SUPABASE_KEY=eyJ...
    
    # Option 2: Create config explicitly
    config = LangChatConfig(
        openai_api_keys=[os.getenv("OPENAI_API_KEY", "your-openai-api-key")],
        openai_model="gpt-4o-mini",
        openai_temperature=0.7,  # Lower temperature for more focused educational responses
        pinecone_api_key=os.getenv("PINECONE_API_KEY", "your-pinecone-api-key"),
        pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", "education-index"),
        supabase_url=os.getenv("SUPABASE_URL", "your-supabase-url"),
        supabase_key=os.getenv("SUPABASE_KEY", "your-supabase-key"),
        # Custom prompts for education domain
        system_prompt_template=EDUCATION_SYSTEM_PROMPT,
        standalone_question_prompt=EDUCATION_STANDALONE_PROMPT,
        # Education-specific settings
        retrieval_k=5,  # Retrieve 5 relevant educational documents
        reranker_top_n=3,  # Rerank to top 3 most relevant
        max_chat_history=20,  # Keep last 20 messages for context
    )
    
    # Initialize LangChat
    # Behind the scenes, this uses:
    # - OpenAILLMService (implements LLMProvider)
    # - PineconeVectorAdapter (implements VectorStoreProvider)
    # - SupabaseAdapter (implements HistoryStore)
    # - FlashrankRerankAdapter (implements RerankerProvider)
    langchat = LangChat(config=config)
    
    # Example educational queries
    queries = [
        "What is photosynthesis and how does it work?",
        "Can you explain the water cycle in simple terms?",
        "What are the main causes of World War I?",
    ]
    
    user_id = "student_001"
    domain = "education"
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Question {i} ---")
        print(f"Student: {query}")
        
        # The response will be automatically displayed in a Rich panel
        result = await langchat.chat(
            query=query,
            user_id=user_id,
            domain=domain,
        )
        
        # Access response metadata programmatically
        print(f"\n✓ Response time: {result['response_time']:.2f}s")
        print(f"✓ Status: {result['status']}")
        
        # Wait a bit between queries
        await asyncio.sleep(1)


# ============================================================================
# Demonstrating Adapter Pattern Benefits
# ============================================================================

async def example_adapter_pattern_explanation():
    """
    This example explains how the adapter pattern works and its benefits.
    
    The adapter pattern allows you to:
    1. Use default providers (current implementation)
    2. Easily swap to alternative providers without changing core code
    3. Create custom providers for specific needs
    """
    
    # Show how the engine uses abstract interfaces
    config = LangChatConfig.from_env()
    langchat = LangChat(config=config)
    
    # The engine internally uses abstract types:
    # - engine.llm: LLMProvider (could be OpenAI, Anthropic, Ollama, etc.)
    # - engine.vector_adapter: VectorStoreProvider (could be Pinecone, Chroma, FAISS, etc.)
    # - engine.history_store: HistoryStore (could be Supabase, PostgreSQL, MongoDB, etc.)
    # - engine.reranker_adapter: RerankerProvider (could be FlashRank, Cohere, etc.)
    

# ============================================================================
# Interactive Educational Chat
# ============================================================================

async def example_interactive_chat():
    """
    Interactive example where you can chat with the educational assistant.
    """
    
    config = LangChatConfig.from_env()
    langchat = LangChat(config=config)
    
    user_id = "interactive_student"
    domain = "education"
    
    while True:
        try:
            query = input("\nYou: ").strip()
            
            if query.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye! Keep learning!")
                break
            
            if not query:
                continue
            
            print("\n🤔 Thinking...")
            result = await langchat.chat(
                query=query,
                user_id=user_id,
                domain=domain,
            )
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {str(e)}")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(example_basic_usage())
