"""
Tests for API routes module.
"""

from unittest.mock import MagicMock, patch

import pytest

from langchat.api.routes import chat, health_check, router


class TestRoutes:
    """Test cases for API routes."""

    def test_router_exists(self):
        """Test that router exists."""
        assert router is not None

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint."""
        result = await health_check()

        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "version" in result

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self):
        """Test that chat endpoint function exists."""
        assert callable(chat)

    @pytest.mark.asyncio
    async def test_chat_endpoint_with_mock_engine(self):
        """Test chat endpoint with mocked engine."""

        # Mock the get_engine dependency
        mock_engine = MagicMock()
        mock_engine.chat = MagicMock(
            return_value={
                "response": "test response",
                "context": [],
            }
        )

        with patch("langchat.api.routes.get_engine", return_value=mock_engine):
            # Mock Form data
            mock_query = "test query"
            mock_user_id = "test-user"
            mock_domain = "default"

            # Call the chat endpoint with mocked form data
            result = await chat(
                query=mock_query,
                userId=mock_user_id,
                domain=mock_domain,
                image=None,
                background_tasks=MagicMock(),
            )

            assert result is not None
            # The result should be a JSONResponse
            assert hasattr(result, "body") or isinstance(result, dict)
