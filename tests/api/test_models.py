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
