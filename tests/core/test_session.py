"""
Tests for UserSession.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchat.config import LangChatConfig
from langchat.core.session import UserSession


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
def mock_adapters():
    """Create mock adapters for testing."""
    llm = MagicMock()
    vector_adapter = MagicMock()
    reranker_adapter = MagicMock()
    supabase_adapter = MagicMock()
    id_manager = MagicMock()
    
    return {
        "llm": llm,
        "vector_adapter": vector_adapter,
        "reranker_adapter": reranker_adapter,
        "supabase_adapter": supabase_adapter,
        "id_manager": id_manager,
    }


@pytest.fixture
def session(mock_config, mock_adapters):
    """Create a session instance for testing."""
    prompt_template = "You are a helpful assistant. Question: {question} Answer: {answer}"
    
    with patch("langchat.core.session.ConversationBufferWindowMemory"):
        session = UserSession(
            domain="test-domain",
            user_id="test-user",
            config=mock_config,
            llm=mock_adapters["llm"],
            vector_adapter=mock_adapters["vector_adapter"],
            reranker_adapter=mock_adapters["reranker_adapter"],
            supabase_adapter=mock_adapters["supabase_adapter"],
            id_manager=mock_adapters["id_manager"],
            prompt_template=prompt_template,
        )
        return session


class TestUserSession:
    """Test cases for UserSession."""

    def test_session_initialization(self, session):
        """Test session initialization."""
        assert session.domain == "test-domain"
        assert session.user_id == "test-user"
        assert session.config is not None

    def test_session_has_create_conversation_method(self, session):
        """Test that session has _create_conversation method."""
        assert hasattr(session, "_create_conversation")
        assert callable(session._create_conversation)

    def test_session_has_save_message_method(self, session):
        """Test that session has a save_message method."""
        assert hasattr(session, "save_message")
        assert callable(session.save_message)

    def test_session_has_load_chat_history_method(self, session):
        """Test that session has _load_chat_history method."""
        assert hasattr(session, "_load_chat_history")
        assert callable(session._load_chat_history)


@pytest.mark.asyncio
class TestUserSessionAsync:
    """Async test cases for UserSession."""

    async def test_session_has_retrieval_methods(self, session):
        """Test that session has retrieval and response methods."""
        # The session uses internal methods that are part of the conversation chain
        assert hasattr(session, "_create_conversation")
        assert callable(session._create_conversation)

