#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import asyncio
import os
from dotenv import load_dotenv

from langchat import LangChat
from langchat.adapters.llm import OpenAI
from langchat.adapters.vector_db import Pinecone
from langchat.adapters.database import Supabase

load_dotenv()

CUSTOM_PROMPT = """You are a helpful assistant. Answer questions clearly.

Context: {context}
History: {chat_history}
Question: {question}
Answer:"""

async def main():
    llm = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    vector_db = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding_model="text-embedding-3-large",
        embedding_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    db = Supabase.from_config(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY")
    )
    
    langchat = LangChat(
        llm=llm,
        vector_db=vector_db,
        db=db,
        prompt_template=CUSTOM_PROMPT
    )
    
    result = await langchat.chat(
        query="Explain quantum computing",
        user_id="user123",
        domain="default"
    )
    
    print(result["response"])

if __name__ == "__main__":
    asyncio.run(main())

