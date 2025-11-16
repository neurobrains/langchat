"""
Tests for PineconeVectorAdapter.
"""

from unittest.mock import MagicMock, patch

from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter


class TestPineconeVectorAdapter:
    """Test cases for PineconeVectorAdapter."""

    @patch("langchat.adapters.vector_db.pinecone_adapter.Pinecone")
    @patch("langchat.adapters.vector_db.pinecone_adapter.OpenAIEmbeddings")
    @patch("langchat.adapters.vector_db.pinecone_adapter.PineconeVectorStore")
    def test_adapter_initialization(self, mock_vector_store, mock_embeddings, mock_pinecone):
        """Test adapter initialization."""
        mock_index = MagicMock()
        mock_pinecone_instance = MagicMock()
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pinecone_instance

        adapter = PineconeVectorAdapter(
            api_key="test-key",
            index_name="test-index",
        )

        assert adapter.api_key == "test-key"
        assert adapter.index_name == "test-index"
        assert adapter.embedding_model == "text-embedding-3-large"

    @patch("langchat.adapters.vector_db.pinecone_adapter.Pinecone")
    @patch("langchat.adapters.vector_db.pinecone_adapter.OpenAIEmbeddings")
    @patch("langchat.adapters.vector_db.pinecone_adapter.PineconeVectorStore")
    def test_adapter_initialization_custom_embedding(
        self, mock_vector_store, mock_embeddings, mock_pinecone
    ):
        """Test adapter initialization with custom embedding model."""
        mock_index = MagicMock()
        mock_pinecone_instance = MagicMock()
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pinecone_instance

        adapter = PineconeVectorAdapter(
            api_key="test-key",
            index_name="test-index",
            embedding_model="text-embedding-ada-002",
        )

        assert adapter.embedding_model == "text-embedding-ada-002"

    @patch("langchat.adapters.vector_db.pinecone_adapter.Pinecone")
    @patch("langchat.adapters.vector_db.pinecone_adapter.OpenAIEmbeddings")
    @patch("langchat.adapters.vector_db.pinecone_adapter.PineconeVectorStore")
    def test_adapter_has_vector_store(self, mock_vector_store, mock_embeddings, mock_pinecone):
        """Test that adapter has vector_store property."""
        mock_index = MagicMock()
        mock_pinecone_instance = MagicMock()
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pinecone_instance

        adapter = PineconeVectorAdapter(
            api_key="test-key",
            index_name="test-index",
        )

        assert hasattr(adapter, "vector_store")
        assert adapter.vector_store is not None
