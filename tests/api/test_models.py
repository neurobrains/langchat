"""
Tests for API models module.
"""

from langchat.api.models import QueryRequest


class TestModels:
    """Test cases for API models."""

    def test_query_request_model(self):
        """Test QueryRequest model."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            domain="default",
        )

        assert request.query == "test query"
        assert request.userId == "test-user"
        assert request.domain == "default"

    def test_query_request_with_domain(self):
        """Test QueryRequest model with custom domain."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            domain="custom-domain",
        )

        assert request.domain == "custom-domain"

    def test_query_request_optional_image(self):
        """Test QueryRequest model with optional image."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            domain="default",
            image=None,
        )

        assert request.image is None

    def test_query_request_with_image(self):
        """Test QueryRequest model with image."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            domain="default",
            image="base64encodedimage",
        )

        assert request.image == "base64encodedimage"
