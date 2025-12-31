#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

from langchat.adapters.llm import OpenAI
from langchat.adapters.vector_db import Pinecone
from langchat.adapters.database import Supabase
from langchat.api.app import create_app

load_dotenv()

def main():
    llm = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "1.0"))
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
    
    app = create_app(
        llm=llm,
        vector_db=vector_db,
        db=db,
        port=int(os.getenv("PORT", "8000"))
    )
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

if __name__ == "__main__":
    main()

