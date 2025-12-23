# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import pytest

from langchat.llm.openai_provider import OpenAI


class TestOpenAILLMService:
    """Test cases for OpenAILLMService."""

    def test_service_initialization(self):
        """Test service initialization."""
        with patch("langchat.llm.openai_provider.ChatOpenAI"):
            service = OpenAI(
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
        with patch("langchat.llm.openai_provider.ChatOpenAI"):
            service = OpenAI(
                model="gpt-4",
                temperature=0.7,
                api_keys=["test-key"],
            )
            assert service.model == "gpt-4"
            assert service.temperature == 0.7

    def test_service_initialization_no_keys(self):
        """Test service initialization with no keys raises error."""
        with patch("langchat.llm.openai_provider.ChatOpenAI"):
            with pytest.raises(ValueError, match="At least one OpenAI API key is required"):
                OpenAI(
                    model="gpt-4",
                    temperature=0.7,
                    api_keys=[],
                )

    def test_service_has_current_llm(self):
        """Test that service has current_llm property."""
        with patch("langchat.llm.openai_provider.ChatOpenAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            service = OpenAI(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["test-key"],
            )
            assert service.current_llm is not None

    def test_service_rotate_key_method(self):
        """Test key rotation method exists."""
        with patch("langchat.llm.openai_provider.ChatOpenAI"):
            service = OpenAI(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["key-1", "key-2"],
            )
            assert hasattr(service, "_rotate_key")
            assert callable(service._rotate_key)

    def test_service_create_llm_method(self):
        """Test _create_llm method exists."""
        with patch("langchat.llm.openai_provider.ChatOpenAI"):
            service = OpenAI(
                model="gpt-4o-mini",
                temperature=1.0,
                api_keys=["test-key"],
            )
            assert hasattr(service, "_create_llm")
            assert callable(service._create_llm)
