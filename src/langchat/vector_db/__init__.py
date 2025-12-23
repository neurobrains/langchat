# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Vector Database Providers - Support for multiple vector databases.
"""

from langchat.vector_db.pinecone_provider import Pinecone, PineconeProvider

__all__ = [
    # New names (recommended)
    "Pinecone",
    # Old names (backward compatibility)
    "PineconeProvider",
]

