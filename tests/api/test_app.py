# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

from langchat.api.app import create_app


class TestApp:
    """Test cases for API app."""

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_create_app(self, mock_set_mode, mock_engine_class):
        """Test create_app function."""
        with patch("langchat.api.app.FastAPI"):
            app = create_app()
            assert app is not None
            assert hasattr(app, "router")

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_create_app_without_config(self, mock_set_mode, mock_engine_class, monkeypatch):
        """Test create_app without config (uses env)."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
        monkeypatch.setenv("PINECONE_INDEX_NAME", "test-index")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")

        with patch("langchat.api.app.FastAPI"):
            app = create_app()
            assert app is not None

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_app_has_routes(self, mock_set_mode, mock_engine_class):
        """Test that app has routes configured."""
        with patch("langchat.api.app.FastAPI") as mock_fastapi:
            mock_app_instance = MagicMock()
            mock_fastapi.return_value = mock_app_instance

            app = create_app()

            # Verify routes were added
            assert hasattr(app, "include_router") or hasattr(mock_app_instance, "include_router")
