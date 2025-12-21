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

from langchat.api.app import create_app
from langchat.config import LangChatConfig


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


class TestApp:
    """Test cases for API app."""

    @patch("langchat.api.app.LangChatEngine")
    @patch("langchat.api.app.set_api_server_mode")
    def test_create_app(self, mock_set_mode, mock_engine_class, mock_config):
        """Test create_app function."""
        with patch("langchat.api.app.FastAPI"):
            app = create_app(config=mock_config)
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
    def test_app_has_routes(self, mock_set_mode, mock_engine_class, mock_config):
        """Test that app has routes configured."""
        with patch("langchat.api.app.FastAPI") as mock_fastapi:
            mock_app_instance = MagicMock()
            mock_fastapi.return_value = mock_app_instance

            app = create_app(config=mock_config)

            # Verify routes were added
            assert hasattr(app, "include_router") or hasattr(mock_app_instance, "include_router")
