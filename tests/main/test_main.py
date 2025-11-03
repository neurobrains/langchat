"""
Tests for LangChat main module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchat.config import LangChatConfig
from langchat.main import LangChat


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


class TestLangChat:
    """Test cases for LangChat."""

    def test_langchat_initialization_with_config(self, mock_config):
        """Test LangChat initialization with provided config."""
        with patch("langchat.main.LangChatEngine"):
            langchat = LangChat(config=mock_config)
            assert langchat.config == mock_config
            assert langchat.engine is not None

    def test_langchat_initialization_without_config(self, monkeypatch):
        """Test LangChat initialization without config (uses env)."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        monkeypatch.setenv("PINECONE_INDEX_NAME", "test-index")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")

        with patch("langchat.main.LangChatEngine"):
            langchat = LangChat()
            assert langchat.config is not None
            assert langchat.engine is not None

    def test_langchat_has_chat_method(self, mock_config):
        """Test that LangChat has a chat method."""
        with patch("langchat.main.LangChatEngine"):
            langchat = LangChat(config=mock_config)
            assert hasattr(langchat, "chat")
            assert callable(langchat.chat)

    def test_langchat_chat_sync_method(self, mock_config):
        """Test that LangChat has a chat_sync method."""
        with patch("langchat.main.LangChatEngine"):
            langchat = LangChat(config=mock_config)
            assert hasattr(langchat, "chat_sync")
            assert callable(langchat.chat_sync)


@pytest.mark.asyncio
class TestLangChatAsync:
    """Async test cases for LangChat."""

    async def test_chat_method_callable(self, mock_config):
        """Test that chat method can be called."""
        with patch("langchat.main.LangChatEngine") as mock_engine_class:
            mock_engine = MagicMock()
            # Mock the async chat method properly
            async def mock_chat(*args, **kwargs):
                return {"response": "test"}
            mock_engine.chat = mock_chat
            mock_engine_class.return_value = mock_engine
            
            langchat = LangChat(config=mock_config)
            
            result = await langchat.chat("test query", "user1")
            
            assert result is not None
            assert isinstance(result, dict)

    async def test_chat_method_with_domain(self, mock_config):
        """Test chat method with custom domain."""
        with patch("langchat.main.LangChatEngine") as mock_engine_class:
            mock_engine = MagicMock()
            # Mock the async chat method properly
            async def mock_chat(*args, **kwargs):
                return {"response": "test"}
            mock_engine.chat = mock_chat
            mock_engine_class.return_value = mock_engine
            
            langchat = LangChat(config=mock_config)
            
            result = await langchat.chat("test query", "user1", domain="custom")
            
            assert result is not None

