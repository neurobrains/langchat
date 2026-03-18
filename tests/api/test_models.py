# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from langchat.api.models import QueryRequest


class TestModels:
    """Test cases for API models."""

    def test_query_request_model(self):
        """Test QueryRequest model."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            platform="default",
        )

        assert request.query == "test query"
        assert request.userId == "test-user"
        assert request.platform == "default"

    def test_query_request_with_platform(self):
        """Test QueryRequest model with custom platform."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            platform="custom-platform",
        )

        assert request.platform == "custom-platform"

    def test_query_request_optional_image(self):
        """Test QueryRequest model with optional image."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            platform="default",
            image=None,
        )

        assert request.image is None

    def test_query_request_with_image(self):
        """Test QueryRequest model with image."""
        request = QueryRequest(
            query="test query",
            userId="test-user",
            platform="default",
            image="base64encodedimage",
        )

        assert request.image == "base64encodedimage"
