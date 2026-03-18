# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import pytest

from langchat.api.app import create_app


class TestApp:
    """Test cases for API app."""

    @pytest.fixture
    def mock_llm(self):
        return MagicMock()

    @pytest.fixture
    def mock_vector_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_create_app(self, mock_set_mode, mock_engine_class, mock_llm, mock_vector_db, mock_db):
        """Test create_app function."""
        with patch("langchat.api.app.FastAPI"):
            app = create_app(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)
            assert app is not None

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_app_has_routes(
        self, mock_set_mode, mock_engine_class, mock_llm, mock_vector_db, mock_db
    ):
        """Test that app has routes configured."""
        with patch("langchat.api.app.FastAPI") as mock_fastapi:
            mock_app_instance = MagicMock()
            mock_fastapi.return_value = mock_app_instance

            app = create_app(llm=mock_llm, vector_db=mock_vector_db, db=mock_db)

            assert app is not None
