# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for the LangChat SDK (sdk.py)."""

from unittest.mock import MagicMock, patch

import pytest

from langchat.sdk import LangChat
from langchat.types import ChatResponse

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm._current_key = "sk-test-key"
    llm.api_keys = iter(["sk-test-key"])
    return llm


@pytest.fixture
def mock_vector_db():
    vdb = MagicMock()
    vdb.api_key = "pc-test-key"
    vdb.index_name = "test-index"
    vdb.embedding_model = "text-embedding-3-large"
    return vdb


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def lc(mock_llm, mock_vector_db, mock_db):
    """LangChat instance with all dependencies mocked."""
    with patch("langchat.sdk.LangChatEngine"):
        return LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestLangChatInit:
    def test_creates_engine(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            mock_engine_cls.assert_called_once()
            assert lc.engine is not None

    def test_forwards_all_kwargs_to_engine(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            LangChat(
                llm=mock_llm,
                vector_db=mock_vector_db,
                db=mock_db,
                prompt_template="You are helpful.",
                max_chat_history=10,
                verbose=True,
            )
            _, kwargs = mock_engine_cls.call_args
            assert kwargs["prompt_template"] == "You are helpful."
            assert kwargs["max_chat_history"] == 10
            assert kwargs["verbose"] is True

    def test_has_required_public_methods(self, lc):
        for method in ("chat", "chat_sync", "get_session", "index", "load_env"):
            assert callable(getattr(lc, method)), f"Missing method: {method}"


# ---------------------------------------------------------------------------
# chat() — returns ChatResponse
# ---------------------------------------------------------------------------


class TestLangChatAsyncChat:
    @pytest.mark.asyncio
    async def test_chat_returns_chat_response(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()

            async def _fake_chat(**kwargs):
                return {
                    "response": "Hello!",
                    "user_id": "alice",
                    "status": "success",
                    "response_time": 0.5,
                    "timestamp": "2025-01-01T00:00:00Z",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = await lc.chat("Hello", user_id="alice")

            assert isinstance(response, ChatResponse)

    @pytest.mark.asyncio
    async def test_chat_response_fields(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()

            async def _fake_chat(**kwargs):
                return {
                    "response": "The answer is 42.",
                    "user_id": "bob",
                    "status": "success",
                    "response_time": 1.23,
                    "timestamp": "2025-06-01T12:00:00Z",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = await lc.chat("What is the answer?", user_id="bob", platform="science")

            assert response.text == "The answer is 42."
            assert response.user_id == "bob"
            assert response.platform == "science"
            assert response.status == "success"
            assert response.response_time == 1.23
            assert response.timestamp == "2025-06-01T12:00:00Z"
            assert response.error is None

    @pytest.mark.asyncio
    async def test_chat_bool_true_on_success(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()

            async def _fake_chat(**kwargs):
                return {
                    "response": "ok",
                    "user_id": "u",
                    "status": "success",
                    "response_time": 0.1,
                    "timestamp": "t",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = await lc.chat("hi", user_id="u")
            assert bool(response) is True

    @pytest.mark.asyncio
    async def test_chat_bool_false_on_error(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()

            async def _fake_chat(**kwargs):
                return {
                    "response": "",
                    "user_id": "u",
                    "status": "error",
                    "response_time": 0.0,
                    "timestamp": "t",
                    "error": "oops",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = await lc.chat("hi", user_id="u")
            assert bool(response) is False
            assert response.error == "oops"

    @pytest.mark.asyncio
    async def test_chat_default_platform_is_default(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            received = {}

            async def _fake_chat(**kwargs):
                received.update(kwargs)
                return {
                    "response": "ok",
                    "user_id": "u",
                    "status": "success",
                    "response_time": 0.0,
                    "timestamp": "t",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = await lc.chat("hi", user_id="u")
            assert response.platform == "default"


# ---------------------------------------------------------------------------
# chat_sync()
# ---------------------------------------------------------------------------


class TestChatSync:
    def test_chat_sync_returns_chat_response(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()

            async def _fake_chat(**kwargs):
                return {
                    "response": "sync!",
                    "user_id": "u",
                    "status": "success",
                    "response_time": 0.1,
                    "timestamp": "t",
                }

            mock_engine.chat = _fake_chat
            mock_engine_cls.return_value = mock_engine

            lc = LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            response = lc.chat_sync("hello", user_id="u")

            assert isinstance(response, ChatResponse)
            assert response.text == "sync!"


# ---------------------------------------------------------------------------
# index() — unified single / multi-file
# ---------------------------------------------------------------------------


class TestIndex:
    def _make_lc(self, mock_llm, mock_vector_db, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.llm = mock_llm
            mock_engine.vector_adapter = mock_vector_db
            mock_engine_cls.return_value = mock_engine
            return LangChat(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)

    def test_index_single_file_calls_single_indexer(self, mock_llm, mock_vector_db, mock_db):
        lc = self._make_lc(mock_llm, mock_vector_db, mock_db)

        with patch("langchat.sdk.DocumentIndexer") as mock_indexer_cls:
            mock_indexer = MagicMock()
            mock_indexer.load_and_index_documents.return_value = {"chunks_indexed": 5}
            mock_indexer_cls.return_value = mock_indexer

            result = lc.index("guide.pdf")

            mock_indexer.load_and_index_documents.assert_called_once_with(
                file_path="guide.pdf",
                chunk_size=1000,
                chunk_overlap=200,
                namespace=None,
                prevent_duplicates=True,
            )
            assert result == {"chunks_indexed": 5}

    def test_index_list_calls_multiple_indexer(self, mock_llm, mock_vector_db, mock_db):
        lc = self._make_lc(mock_llm, mock_vector_db, mock_db)

        with patch("langchat.sdk.DocumentIndexer") as mock_indexer_cls:
            mock_indexer = MagicMock()
            mock_indexer.load_and_index_multiple_documents.return_value = {
                "total_chunks_indexed": 10
            }
            mock_indexer_cls.return_value = mock_indexer

            result = lc.index(["a.pdf", "b.pdf"])

            mock_indexer.load_and_index_multiple_documents.assert_called_once_with(
                file_paths=["a.pdf", "b.pdf"],
                chunk_size=1000,
                chunk_overlap=200,
                namespace=None,
                prevent_duplicates=True,
            )
            assert result == {"total_chunks_indexed": 10}

    def test_index_passes_custom_options(self, mock_llm, mock_vector_db, mock_db):
        lc = self._make_lc(mock_llm, mock_vector_db, mock_db)

        with patch("langchat.sdk.DocumentIndexer") as mock_indexer_cls:
            mock_indexer = MagicMock()
            mock_indexer.load_and_index_documents.return_value = {}
            mock_indexer_cls.return_value = mock_indexer

            lc.index("file.pdf", chunk_size=500, chunk_overlap=50, namespace="v2")

            mock_indexer.load_and_index_documents.assert_called_once_with(
                file_path="file.pdf",
                chunk_size=500,
                chunk_overlap=50,
                namespace="v2",
                prevent_duplicates=True,
            )

    def test_index_raises_without_vector_db(self, mock_llm, mock_db):
        with patch("langchat.sdk.LangChatEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.vector_adapter = None
            mock_engine.llm = mock_llm
            mock_engine_cls.return_value = mock_engine
            lc = LangChat(llm=mock_llm, vector_db=MagicMock(), db=mock_db)
            lc.engine.vector_adapter = None

            with pytest.raises(ValueError, match="No vector_db adapter"):
                lc.index("file.pdf")


# ---------------------------------------------------------------------------
# load_env()
# ---------------------------------------------------------------------------


class TestLoadEnv:
    def test_raises_when_no_dotenv_file(self, lc):
        with patch("langchat.sdk.Path") as mock_path_cls:
            mock_path_cls.return_value.exists.return_value = False
            with pytest.raises(FileNotFoundError):
                lc.load_env()

    def test_loads_dotenv_when_file_exists(self, lc):
        with (
            patch("langchat.sdk.Path") as mock_path_cls,
            patch("langchat.sdk.load_dotenv") as mock_load,
        ):
            mock_path_cls.return_value.exists.return_value = True
            lc.load_env()
            mock_load.assert_called_once()
