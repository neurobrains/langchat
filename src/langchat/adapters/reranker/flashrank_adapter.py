"""
Flashrank reranker adapter.
"""

# mypy: disable-error-code=no-redef

from typing import Any

from flashrank import Ranker


def _import_flashrank_rerank() -> Any:  # type: ignore[no-redef]
    """Import FlashrankRerank with fallback to different import paths."""
    try:
        from langchain_community.document_compressors.flashrank_rerank import (
            FlashrankRerank,
        )

        return FlashrankRerank
    except ImportError:
        try:
            from langchain.retrievers.document_compressors.flashrank_rerank import (
                FlashrankRerank,  # type: ignore[no-redef]
            )

            return FlashrankRerank
        except ImportError:
            try:
                from langchain_community.cross_encoders import (
                    FlashrankRerank,  # type: ignore[no-redef]
                )

                return FlashrankRerank
            except ImportError:
                try:
                    from langchain.retrievers.document_compressors import (
                        FlashrankRerank,  # type: ignore[no-redef]
                    )

                    return FlashrankRerank
                except ImportError as err:
                    raise ImportError(
                        "Could not import FlashrankRerank. Please install langchain and langchain-community: pip install langchain langchain-community"
                    ) from err


def _import_contextual_compression_retriever() -> Any:
    """Import ContextualCompressionRetriever with fallback to different import paths."""
    try:
        from langchain.retrievers.contextual_compression import (
            ContextualCompressionRetriever,
        )

        return ContextualCompressionRetriever
    except ImportError:
        try:
            from langchain_core.retrievers import (  # type: ignore[attr-defined,no-redef]
                ContextualCompressionRetriever,
            )

            return ContextualCompressionRetriever
        except ImportError as err:
            raise ImportError(
                "Could not import ContextualCompressionRetriever. Please install langchain: pip install langchain"
            ) from err


# Import with fallback logic
FlashrankRerank = _import_flashrank_rerank()
ContextualCompressionRetriever = _import_contextual_compression_retriever()


class FlashrankRerankAdapter:
    """
    Adapter for Flashrank reranker.
    """

    def __init__(
        self,
        model_name: str = "ms-marco-MiniLM-L-12-v2",
        cache_dir: str = "rerank_models",
        top_n: int = 3,
    ):
        """
        Initialize Flashrank reranker adapter.

        Args:
            model_name: Flashrank model name
            cache_dir: Directory to cache the model
            top_n: Number of top documents to return after reranking
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.top_n = top_n

        # Initialize ranker
        self.ranker = Ranker(model_name=model_name, cache_dir=cache_dir)

        # Initialize compressor
        self.compressor = FlashrankRerank(client=self.ranker, top_n=top_n)

    def create_compression_retriever(self, base_retriever):
        """
        Create a contextual compression retriever.

        Args:
            base_retriever: Base retriever to compress

        Returns:
            ContextualCompressionRetriever instance
        """
        return ContextualCompressionRetriever(
            base_compressor=self.compressor, base_retriever=base_retriever
        )
