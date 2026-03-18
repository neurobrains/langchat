#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
FastAPI server example — production REST API.

Exposes a /chat endpoint that any frontend or mobile app can call.
All providers read credentials from environment variables automatically.

Setup
-----
    OPENAI_API_KEY=sk-...
    PINECONE_API_KEY=pc-...
    PINECONE_INDEX_NAME=my-index
    SUPABASE_URL=https://yourproject.supabase.co
    SUPABASE_KEY=your-service-role-key
    PORT=8000           (optional, default 8000)

Run
---
    python examples/server.py

    # or with uv:
    uv run examples/server.py

Endpoints
---------
    POST /chat      { "query": "...", "userId": "...", "domain": "..." }
    GET  /health    returns service status
    GET  /frontend  serves the built-in chat UI
"""

import os

import uvicorn

from langchat.api.app import create_app
from langchat.providers import OpenAI, Pinecone, Supabase

app = create_app(
    llm=OpenAI(os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
    vector_db=Pinecone(os.getenv("PINECONE_INDEX_NAME", "my-index")),
    db=Supabase(),
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting LangChat server on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
