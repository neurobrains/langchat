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

from langchat.adapters.services.openai_service import OpenAILLMService


class TestOpenAILLMService:
    """Test cases for OpenAILLMService."""

    def test_service_initialization(self):
        """Test service initialization."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI"):
            service = OpenAILLMService(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["test-key-1", "test-key-2"],
            )
            assert service.model == "gpt-4o-mini"
            assert service.temperature == 1.0
            # Test that api_keys is a cycle iterator (can't directly get length)
            # Instead, test that it has items by checking if current_key is set
            assert service.current_key is not None

    def test_service_initialization_single_key(self):
        """Test service initialization with single key."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI"):
            service = OpenAILLMService(
                model="gpt-4",
                temperature=0.7,
                api_keys=["test-key"],
            )
            assert service.model == "gpt-4"
            assert service.temperature == 0.7

    def test_service_initialization_no_keys(self):
        """Test service initialization with no keys raises error."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI"):
            with pytest.raises(ValueError, match="No API keys provided"):
                OpenAILLMService(
                    model="gpt-4",
                    temperature=0.7,
                    api_keys=[],
                )

    def test_service_has_current_llm(self):
        """Test that service has current_llm property."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            service = OpenAILLMService(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["test-key"],
            )
            assert service.current_llm is not None

    def test_service_rotate_key_method(self):
        """Test key rotation method exists."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI"):
            service = OpenAILLMService(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["key-1", "key-2"],
            )
            assert hasattr(service, "_rotate_key")
            assert callable(service._rotate_key)

    def test_service_create_llm_method(self):
        """Test _create_llm method exists."""
        with patch("langchat.adapters.services.openai_service.ChatOpenAI"):
            service = OpenAILLMService(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["test-key"],
            )
            assert hasattr(service, "_create_llm")
            assert callable(service._create_llm)
