# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Reranker Providers - Support for multiple reranking services.
"""

from langchat.reranker.flashrank_provider import Flashrank, FlashrankProvider

__all__ = [
    # New names (recommended)
    "Flashrank",
    # Old names (backward compatibility)
    "FlashrankProvider",
]

