#!/usr/bin/env python3
# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Document indexing example — building a knowledge base.

Shows how to index documents into Pinecone before running a chatbot.
Supports PDF, TXT, CSV, and other formats via docsuite.

Typical workflow
----------------
1. Run this script once to populate the vector store.
2. Run basic.py (or server.py) to start answering questions.

Setup
-----
    OPENAI_API_KEY=sk-...
    PINECONE_API_KEY=pc-...
    PINECONE_INDEX_NAME=company-docs
    SUPABASE_URL=https://yourproject.supabase.co
    SUPABASE_KEY=your-service-role-key

Run
---
    python examples/rag_indexing.py
"""

from pathlib import Path

from langchat import LangChat
from langchat.providers import OpenAI, Pinecone, Supabase

# ---------------------------------------------------------------------------
# Build client (DB adapter required even for indexing-only scripts)
# ---------------------------------------------------------------------------

lc = LangChat(
    llm=OpenAI("gpt-4o-mini"),
    vector_db=Pinecone("company-docs"),
    db=Supabase(),
)

# ---------------------------------------------------------------------------
# Index a single file
# ---------------------------------------------------------------------------


def index_single():
    print("Indexing single file...")
    result = lc.index(
        "docs/product-manual.pdf",
        chunk_size=1000,
        chunk_overlap=200,
    )
    print(f"  Indexed : {result.get('chunks_indexed', 0)} chunks")
    print(f"  Skipped : {result.get('chunks_skipped', 0)} duplicates")


# ---------------------------------------------------------------------------
# Index an entire folder of documents
# ---------------------------------------------------------------------------


def index_folder(folder: str = "docs/"):
    supported = [".pdf", ".txt", ".csv"]
    files = [str(p) for p in Path(folder).rglob("*") if p.suffix.lower() in supported]

    if not files:
        print(f"No supported documents found in {folder}")
        return

    print(f"Indexing {len(files)} file(s) from {folder}...")
    result = lc.index(
        files,
        chunk_size=800,
        chunk_overlap=100,
        namespace="v1",  # use namespaces to version your index
        prevent_duplicates=True,  # safe to re-run — existing chunks are skipped
    )
    print(f"  Indexed : {result.get('total_chunks_indexed', 0)} chunks")
    print(f"  Skipped : {result.get('total_chunks_skipped', 0)} duplicates")
    print(f"  Files   : {result.get('files_processed', len(files))}")


# ---------------------------------------------------------------------------
# Index with multiple namespaces (e.g. per department)
# ---------------------------------------------------------------------------


def index_by_department():
    departments = {
        "hr": ["docs/hr/handbook.pdf", "docs/hr/leave-policy.pdf"],
        "legal": ["docs/legal/terms.pdf", "docs/legal/privacy.pdf"],
        "product": ["docs/product/manual.pdf", "docs/product/faq.txt"],
    }

    for dept, files in departments.items():
        existing = [f for f in files if Path(f).exists()]
        if not existing:
            print(f"[{dept}] No files found, skipping.")
            continue

        result = lc.index(existing, namespace=dept)
        total = result.get("total_chunks_indexed", result.get("chunks_indexed", 0))
        print(f"[{dept}] Indexed {total} chunks")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Choose the indexing strategy that fits your use case:
    index_single()  # one file
    # index_folder()       # entire docs/ directory
    # index_by_department()  # multiple namespaces
