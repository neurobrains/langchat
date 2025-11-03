"""
Supabase adapter for database operations.
"""

from typing import Optional
from supabase import create_client, Client


class SupabaseAdapter:
    """
    Adapter for Supabase database operations.
    """

    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL
            key: Supabase API key
        """
        self.url = url
        self.key = key
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """
        Get or create Supabase client.
        """
        if self._client is None:
            self._client = create_client(self.url, self.key)
        return self._client

    @classmethod
    def from_config(cls, supabase_url: str, supabase_key: str) -> "SupabaseAdapter":
        """
        Create adapter from configuration.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key

        Returns:
            SupabaseAdapter instance
        """
        return cls(url=supabase_url, key=supabase_key)
