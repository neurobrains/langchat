# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import pytest

from langchat.core.prompts import (
    create_standalone_question_prompt,
    generate_standalone_question,
)


class TestPrompts:
    """Test cases for prompts."""

    def test_create_standalone_question_prompt_exists(self):
        """Test that create_standalone_question_prompt function exists."""
        assert callable(create_standalone_question_prompt)

    def test_create_standalone_question_prompt_default(self):
        """Test creating prompt with default template."""
        with patch("langchat.core.prompts.PromptTemplate"):
            prompt = create_standalone_question_prompt()
            assert prompt is not None

    def test_create_standalone_question_prompt_custom(self):
        """Test creating prompt with custom template."""
        custom_template = "Custom template: {question}"
        with patch("langchat.core.prompts.PromptTemplate"):
            prompt = create_standalone_question_prompt(custom_prompt=custom_template)
            assert prompt is not None

    def test_generate_standalone_question_exists(self):
        """Test that generate_standalone_question function exists."""
        assert callable(generate_standalone_question)


@pytest.mark.asyncio
class TestPromptsAsync:
    """Async test cases for prompts."""

    async def test_generate_standalone_question_basic(self):
        """Test basic standalone question generation."""
        chat_history = [
            ("What is Python?", "Python is a programming language."),
        ]
        query = "Tell me more about it"

        # New implementation calls llm.current_llm.ainvoke([HumanMessage(...)]), provider-agnostic.
        mock_llm = MagicMock()
        mock_current_llm = MagicMock()

        class _Resp:
            content = "Tell me more about Python"

        async def _ainvoke(*args, **kwargs):
            return _Resp()

        mock_current_llm.ainvoke = _ainvoke
        mock_llm.current_llm = mock_current_llm

        result = await generate_standalone_question(
            query=query,
            chat_history=chat_history,
            llm=mock_llm,
        )

        assert isinstance(result, str)
        assert len(result) > 0

    async def test_generate_standalone_question_no_history(self):
        """Test standalone question generation with no history."""
        chat_history = []
        query = "What is Python?"

        mock_llm = MagicMock()
        mock_current_llm = MagicMock()

        class _Resp:
            content = query

        async def _ainvoke(*args, **kwargs):
            return _Resp()

        mock_current_llm.ainvoke = _ainvoke
        mock_llm.current_llm = mock_current_llm

        result = await generate_standalone_question(
            query=query,
            chat_history=chat_history,
            llm=mock_llm,
        )

        assert isinstance(result, str)
        assert len(result) > 0
