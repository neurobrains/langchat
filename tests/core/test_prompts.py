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

        mock_llm = MagicMock()
        mock_llm.model = "gpt-4o-mini"
        mock_llm.temperature = 1.0
        mock_llm.current_key = "test-key"

        with patch("langchat.core.prompts.ChatOpenAI"), patch(
            "langchat.core.prompts.LLMChain"
        ) as mock_chain:
            mock_chain_instance = MagicMock()

            # Mock the async ainvoke method properly
            async def mock_ainvoke(*args, **kwargs):
                return {"standalone_question": "Tell me more about Python"}

            mock_chain_instance.ainvoke = mock_ainvoke
            mock_chain.return_value = mock_chain_instance

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
        mock_llm.model = "gpt-4o-mini"
        mock_llm.temperature = 1.0
        mock_llm.current_key = "test-key"

        with patch("langchat.core.prompts.ChatOpenAI"), patch(
            "langchat.core.prompts.LLMChain"
        ) as mock_chain:
            mock_chain_instance = MagicMock()

            # Mock the async ainvoke method properly
            async def mock_ainvoke(*args, **kwargs):
                return {"standalone_question": query}

            mock_chain_instance.ainvoke = mock_ainvoke
            mock_chain.return_value = mock_chain_instance

            result = await generate_standalone_question(
                query=query,
                chat_history=chat_history,
                llm=mock_llm,
            )

            assert isinstance(result, str)
            assert len(result) > 0
