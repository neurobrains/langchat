# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Pinecone vector database provider."""

from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter


class Pinecone(PineconeVectorAdapter):
    """
    Pinecone vector database provider.

    High-performance vector database optimized for similarity search.
    """

    pass


__all__ = ["Pinecone"]
