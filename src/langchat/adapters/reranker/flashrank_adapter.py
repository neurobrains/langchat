"""
Flashrank reranker adapter.
"""

from flashrank import Ranker

# Fix langchain imports - handle different versions
# Use the new recommended import path first to avoid deprecation warnings
try:
    from langchain_community.document_compressors.flashrank_rerank import (
        FlashrankRerank,
    )
except ImportError:
    try:
        from langchain.retrievers.document_compressors.flashrank_rerank import (
            FlashrankRerank,
        )
    except ImportError:
        try:
            from langchain_community.cross_encoders import FlashrankRerank
        except ImportError:
            try:
                from langchain.retrievers.document_compressors import FlashrankRerank
            except ImportError:
                raise ImportError(
                    "Could not import FlashrankRerank. Please install langchain and langchain-community: pip install langchain langchain-community"
                )

try:
    from langchain.retrievers.contextual_compression import (
        ContextualCompressionRetriever,
    )
except ImportError:
    try:
        from langchain_core.retrievers import ContextualCompressionRetriever
    except ImportError:
        raise ImportError(
            "Could not import ContextualCompressionRetriever. Please install langchain: pip install langchain"
        )

from langchat.logger import logger


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
