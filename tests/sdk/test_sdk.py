# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import pytest

from langchat.sdk import LangChat


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    return MagicMock()


@pytest.fixture
def mock_vector_db():
    """Create a mock vector DB for testing."""
    return MagicMock()


@pytest.fixture
def mock_db():
    """Create a mock DB for testing."""
    return MagicMock()


class TestLangChat:
    """Test cases for LangChat."""

    def test_langchat_initialization(self, mock_llm, mock_vector_db, mock_db):
        """Test LangChat initialization with provided adapters."""
        with patch("langchat.sdk.LangChatEngine"):
            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert langchat.engine is not None

    def test_langchat_has_chat_method(self, mock_llm, mock_vector_db, mock_db):
        """Test that LangChat has a chat method."""
        with patch("langchat.sdk.LangChatEngine"):
            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert hasattr(langchat, "chat")
            assert callable(langchat.chat)

    def test_langchat_chat_sync_method(self, mock_llm, mock_vector_db, mock_db):
        """Test that LangChat has a chat_sync method."""
        with patch("langchat.sdk.LangChatEngine"):
            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert hasattr(langchat, "chat_sync")
            assert callable(langchat.chat_sync)

    def test_langchat_load_env_method(self, mock_llm, mock_vector_db, mock_db):
        """Test that LangChat has a load_env method."""
        with patch("langchat.sdk.LangChatEngine"):
            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert langchat.engine is not None
            # Mock Path(".env").exists() to return False
            with patch("langchat.sdk.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = False
                mock_path_class.return_value = mock_path_instance
                with pytest.raises(FileNotFoundError):
                    langchat.load_env()


@pytest.mark.asyncio
class TestLangChatAsync:
    """Async test cases for LangChat."""

    async def test_chat_method_callable(self, mock_llm, mock_vector_db, mock_db):
        """Test that chat method can be called."""
        with patch("langchat.sdk.LangChatEngine") as mock_engine_class:
            mock_engine = MagicMock()

            # Mock the async chat method properly
            async def mock_chat(*args, **kwargs):
                return {"response": "test"}

            mock_engine.chat = mock_chat
            mock_engine_class.return_value = mock_engine

            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)

            result = await langchat.chat("test query", "user1")

            assert result is not None
            assert isinstance(result, dict)

    async def test_chat_method_with_domain(self, mock_llm, mock_vector_db, mock_db):
        """Test chat method with custom domain."""
        with patch("langchat.sdk.LangChatEngine") as mock_engine_class:
            mock_engine = MagicMock()

            # Mock the async chat method properly
            async def mock_chat(*args, **kwargs):
                return {"response": "test"}

            mock_engine.chat = mock_chat
            mock_engine_class.return_value = mock_engine

            langchat = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)

            result = await langchat.chat("test query", "user1", domain="custom")

            assert result is not None
