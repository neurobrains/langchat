# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Reranker Providers for improved search results."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter

if TYPE_CHECKING:
    from langchat.core.config import LangChatConfig


class Flashrank(FlashrankRerankAdapter):
    """
    Flashrank reranker provider.

    Wrapper around FlashrankRerankAdapter for cleaner API.
    """
    pass


def create_reranker_provider(
    provider: str = "flashrank",
    config: LangChatConfig | None = None,
    **kwargs: Any
) -> Any:
    """
    Create a reranker provider for improved search results.

    Args:
        provider: Provider name ("flashrank", etc.)
        config: LangChatConfig instance
        **kwargs: Provider-specific arguments

    Returns:
        Reranker provider instance

    Example:
        ```python
        # From config
        reranker = create_reranker_provider("flashrank", config=config)

        # Explicit parameters
        reranker = create_reranker_provider(
            "flashrank",
            model_name="ms-marco-MiniLM-L-12-v2",
            cache_dir="rerank_models",
            top_n=3
        )
        ```
    """
    provider = provider.strip().lower()

    if provider == "flashrank":
        model_name = kwargs.get("model_name") or (config.reranker_model if config else "ms-marco-MiniLM-L-12-v2")
        cache_dir = kwargs.get("cache_dir") or (config.reranker_cache_dir if config else "rerank_models")
        top_n = kwargs.get("top_n") or (config.reranker_top_n if config else 3)

        return Flashrank(
            model_name=model_name,
            cache_dir=cache_dir,
            top_n=top_n,
        )

    else:
        raise ValueError(f"Unknown reranker provider: {provider}. Supported: flashrank")


__all__ = ["Flashrank", "create_reranker_provider"]


# Backward compatibility
FlashrankProvider = Flashrank

