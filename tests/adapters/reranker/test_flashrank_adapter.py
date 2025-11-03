"""
Tests for FlashrankRerankAdapter.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter


class TestFlashrankRerankAdapter:
    """Test cases for FlashrankRerankAdapter."""

    @patch("langchat.adapters.reranker.flashrank_adapter.Ranker")
    @patch("langchat.adapters.reranker.flashrank_adapter.FlashrankRerank")
    @patch("langchat.adapters.reranker.flashrank_adapter.ContextualCompressionRetriever")
    def test_adapter_initialization_default(self, mock_compression, mock_rerank, mock_ranker):
        """Test adapter initialization with default model."""
        mock_ranker_instance = MagicMock()
        mock_ranker.return_value = mock_ranker_instance
        
        adapter = FlashrankRerankAdapter()
        
        assert adapter.model_name == "ms-marco-MiniLM-L-12-v2"
        assert adapter.top_n == 3

    @patch("langchat.adapters.reranker.flashrank_adapter.Ranker")
    @patch("langchat.adapters.reranker.flashrank_adapter.FlashrankRerank")
    @patch("langchat.adapters.reranker.flashrank_adapter.ContextualCompressionRetriever")
    def test_adapter_initialization_custom_model(self, mock_compression, mock_rerank, mock_ranker):
        """Test adapter initialization with custom model."""
        mock_ranker_instance = MagicMock()
        mock_ranker.return_value = mock_ranker_instance
        
        adapter = FlashrankRerankAdapter(
            model_name="custom-model",
            top_n=5,
        )
        
        assert adapter.model_name == "custom-model"
        assert adapter.top_n == 5

    @patch("langchat.adapters.reranker.flashrank_adapter.Ranker")
    @patch("langchat.adapters.reranker.flashrank_adapter.FlashrankRerank")
    @patch("langchat.adapters.reranker.flashrank_adapter.ContextualCompressionRetriever")
    def test_adapter_has_create_compression_retriever(self, mock_compression, mock_rerank, mock_ranker):
        """Test that adapter has create_compression_retriever method."""
        mock_ranker_instance = MagicMock()
        mock_ranker.return_value = mock_ranker_instance
        
        adapter = FlashrankRerankAdapter()
        
        assert hasattr(adapter, "create_compression_retriever")
        assert callable(adapter.create_compression_retriever)

