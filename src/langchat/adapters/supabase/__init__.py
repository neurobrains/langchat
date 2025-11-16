"""
Supabase adapters module.
"""

from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter

__all__ = ["SupabaseAdapter", "IDManager"]
