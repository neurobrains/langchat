# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Supabase database provider."""

from langchat.adapters.database.supabase_adapter import SupabaseAdapter


class Supabase(SupabaseAdapter):
    """
    Supabase database provider.

    PostgreSQL-based database with real-time capabilities.
    """

    pass


__all__ = ["Supabase"]
