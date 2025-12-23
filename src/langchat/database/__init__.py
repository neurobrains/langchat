# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Database Providers - Support for multiple databases for chat history storage.
"""

from langchat.database.supabase_provider import Supabase, SupabaseProvider

__all__ = [
    # New names (recommended)
    "Supabase",
    # Old names (backward compatibility)
    "SupabaseProvider",
]

