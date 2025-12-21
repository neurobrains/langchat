# Copyright (c) 2025 NeuroBrain Co Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from unittest.mock import MagicMock, patch

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
    def test_adapter_has_create_compression_retriever(
        self, mock_compression, mock_rerank, mock_ranker
    ):
        """Test that adapter has create_compression_retriever method."""
        mock_ranker_instance = MagicMock()
        mock_ranker.return_value = mock_ranker_instance

        adapter = FlashrankRerankAdapter()

        assert hasattr(adapter, "create_compression_retriever")
        assert callable(adapter.create_compression_retriever)
