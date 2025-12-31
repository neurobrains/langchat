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

async def main():
    llm = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=1.0
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
        db=db
    )
    
    result = await langchat.chat(
        query="What is machine learning?",
        user_id="user123",
        domain="default"
    )
    
    print(result["response"])

if __name__ == "__main__":
    asyncio.run(main())

