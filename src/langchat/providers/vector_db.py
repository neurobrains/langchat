# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Vector Database Providers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter

if TYPE_CHECKING:
    from langchat.core.config import LangChatConfig


class PineconeProvider(PineconeVectorAdapter):
    """
    Pinecone vector database provider.

    Wrapper around PineconeVectorAdapter for cleaner API.
    """
    pass


def create_vector_db_provider(
    provider: str = "pinecone",
    config: LangChatConfig | None = None,
    **kwargs: Any
) -> Any:
    """
    Create a vector database provider.

    Args:
        provider: Provider name ("pinecone", etc.)
        config: LangChatConfig instance
        **kwargs: Provider-specific arguments

    Returns:
        Vector DB provider instance

    Example:
        ```python
        # From config
        vectordb = create_vector_db_provider("pinecone", config=config)

        # Explicit parameters
        vectordb = create_vector_db_provider(
            "pinecone",
            api_key="...",
            index_name="my-index",
            embedding_model="text-embedding-3-large",
            embedding_api_key="..."
        )
        ```
    """
    provider = provider.strip().lower()

    if provider == "pinecone":
        api_key = kwargs.get("api_key") or (config.pinecone_api_key if config else None)
        index_name = kwargs.get("index_name") or (config.pinecone_index_name if config else None)
        embedding_model = kwargs.get("embedding_model") or (config.openai_embedding_model if config else "text-embedding-3-large")
        embedding_api_key = kwargs.get("embedding_api_key") or (config.openai_api_keys[0] if config and config.openai_api_keys else None)

        if not api_key or not index_name:
            raise ValueError("Pinecone api_key and index_name are required")

        return PineconeProvider(
            api_key=api_key,
            index_name=index_name,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )

    else:
        raise ValueError(f"Unknown vector DB provider: {provider}. Supported: pinecone")


__all__ = ["PineconeProvider", "create_vector_db_provider"]

