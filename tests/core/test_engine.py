# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import pytest

from langchat.core.engine import LangChatEngine


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
    mock_client = MagicMock()
    return MagicMock(client=mock_client)


@pytest.fixture
def engine(mock_llm, mock_vector_db, mock_db):
    """Create an engine instance with mocked dependencies."""
    with patch("langchat.core.engine.FlashrankRerankAdapter"), patch(
        "langchat.core.engine.IDManager"
    ):
        engine = LangChatEngine(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
        return engine


class TestLangChatEngine:
    """Test cases for LangChatEngine."""

    def test_engine_initialization(self, mock_llm, mock_vector_db, mock_db):
        """Test engine initialization with provided adapters."""
        with patch("langchat.core.engine.FlashrankRerankAdapter"), patch(
            "langchat.core.engine.IDManager"
        ):
            engine = LangChatEngine(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert engine.llm == mock_llm
            assert engine.vector_adapter == mock_vector_db
            assert engine.history_store == mock_db

    def test_engine_initialization_requires_llm(self):
        """Test engine initialization requires LLM."""
        mock_vector_db = MagicMock()
        mock_db = MagicMock(client=MagicMock())
        with pytest.raises(ValueError, match="LLM provider is required"):
            LangChatEngine(vector_db=mock_vector_db, db=mock_db)

    def test_engine_initialization_requires_vector_db(self, mock_llm):
        """Test engine initialization requires vector DB."""
        mock_db = MagicMock(client=MagicMock())
        with pytest.raises(ValueError, match="Vector database adapter is required"):
            LangChatEngine(llm=mock_llm, db=mock_db)

    def test_engine_initialization_requires_db(self, mock_llm):
        """Test engine initialization requires DB."""
        mock_vector_db = MagicMock()
        with pytest.raises(ValueError, match="Database adapter is required"):
            LangChatEngine(llm=mock_llm, vector_db=mock_vector_db)

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
        # Mock the session and its conversation
        mock_session = MagicMock()
        mock_conversation = MagicMock()
        mock_result = MagicMock()
        mock_result.get.return_value = "test response"
        mock_conversation.ainvoke = MagicMock(return_value=mock_result)
        mock_session.conversation = mock_conversation
        mock_session.chat_history = []
        engine.get_session = MagicMock(return_value=mock_session)

        # Mock generate_standalone_question
        with patch("langchat.core.engine.generate_standalone_question") as mock_gen:
            mock_gen.return_value = "test query"
            result = await engine.chat("test query", "user1")

        assert result is not None
        assert "response" in result
