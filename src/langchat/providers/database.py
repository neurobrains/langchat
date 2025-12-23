# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Database Providers for chat history and metadata storage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchat.adapters.db.supabase_adapter import SupabaseAdapter

if TYPE_CHECKING:
    from langchat.core.config import LangChatConfig


class SupabaseProvider(SupabaseAdapter):
    """
    Supabase database provider.

    Wrapper around SupabaseAdapter for cleaner API.
    """
    pass


def create_database_provider(
    provider: str = "supabase",
    config: LangChatConfig | None = None,
    **kwargs: Any
) -> Any:
    """
    Create a database provider for chat history storage.

    Args:
        provider: Provider name ("supabase", etc.)
        config: LangChatConfig instance
        **kwargs: Provider-specific arguments

    Returns:
        Database provider instance

    Example:
        ```python
        # From config
        db = create_database_provider("supabase", config=config)

        # Explicit parameters
        db = create_database_provider(
            "supabase",
            supabase_url="https://...",
            supabase_key="..."
        )
        ```
    """
    provider = provider.strip().lower()

    if provider == "supabase":
        supabase_url = kwargs.get("supabase_url") or (config.supabase_url if config else None)
        supabase_key = kwargs.get("supabase_key") or (config.supabase_key if config else None)

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key are required")

        return SupabaseProvider.from_config(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
        )

    else:
        raise ValueError(f"Unknown database provider: {provider}. Supported: supabase")


__all__ = ["SupabaseProvider", "create_database_provider"]

