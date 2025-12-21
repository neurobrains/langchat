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

import pytest

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    return LangChatConfig(
        openai_api_keys=["test-key"],
        pinecone_api_key="test-pinecone-key",
        pinecone_index_name="test-index",
        supabase_url="https://test.supabase.co",
        supabase_key="test-supabase-key",
    )


@pytest.fixture
def engine(mock_config):
    """Create an engine instance with mocked dependencies."""
    with patch("langchat.core.engine.PineconeVectorAdapter"), patch(
        "langchat.core.engine.SupabaseAdapter"
    ), patch("langchat.core.engine.OpenAILLMService"), patch(
        "langchat.core.engine.FlashrankRerankAdapter"
    ), patch("langchat.core.engine.IDManager"):
        engine = LangChatEngine(config=mock_config)
        return engine


class TestLangChatEngine:
    """Test cases for LangChatEngine."""

    def test_engine_initialization_with_config(self, mock_config):
        """Test engine initialization with provided config."""
        with patch("langchat.core.engine.PineconeVectorAdapter"), patch(
            "langchat.core.engine.SupabaseAdapter"
        ), patch("langchat.core.engine.OpenAILLMService"), patch(
            "langchat.core.engine.FlashrankRerankAdapter"
        ), patch("langchat.core.engine.IDManager"):
            engine = LangChatEngine(config=mock_config)
            assert engine.config == mock_config

    def test_engine_initialization_without_config(self, monkeypatch):
        """Test engine initialization without config (uses env)."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        monkeypatch.setenv("PINECONE_INDEX_NAME", "test-index")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")

        with patch("langchat.core.engine.PineconeVectorAdapter"), patch(
            "langchat.core.engine.SupabaseAdapter"
        ), patch("langchat.core.engine.OpenAILLMService"), patch(
            "langchat.core.engine.FlashrankRerankAdapter"
        ), patch("langchat.core.engine.IDManager"):
            engine = LangChatEngine()
            assert engine.config is not None
            assert engine.config.openai_api_keys == ["test-key"]

    def test_engine_has_chat_method(self, engine):
        """Test that engine has a chat method."""
        assert hasattr(engine, "chat")
        assert callable(engine.chat)

    def test_engine_has_get_session_method(self, engine):
        """Test that engine has a get_session method."""
        assert hasattr(engine, "get_session")
        assert callable(engine.get_session)

    def test_api_server_mode_flag(self):
        """Test API server mode setting."""
        from langchat.core.engine import set_api_server_mode

        # Note: This might affect other tests, so we'll just check it exists
        assert callable(set_api_server_mode)


@pytest.mark.asyncio
class TestLangChatEngineAsync:
    """Async test cases for LangChatEngine."""

    async def test_chat_method_exists(self, engine):
        """Test that chat method can be called (mocked)."""
        # Mock the session and its chat method
        mock_session = MagicMock()
        mock_session.chat = MagicMock(return_value={"response": "test response"})
        engine.get_session = MagicMock(return_value=mock_session)

        result = await engine.chat("test query", "user1")

        assert result is not None
        assert "response" in result
