# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""OpenAI LLM Provider."""

from itertools import cycle
from typing import List, Optional

from langchain_openai import ChatOpenAI

from langchat.adapters.logger import logger


class OpenAI:
    """
    OpenAI LLM provider with automatic API key rotation and retry logic.

    Supports all OpenAI models including GPT-4, GPT-3.5, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_keys: Optional[List[str]] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 1.0,
        max_retries_per_key: int = 2,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: Single OpenAI API key (or use api_keys for multiple)
            api_keys: List of OpenAI API keys for rotation
            model: OpenAI model name (e.g., "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo")
            temperature: Model temperature (0.0 to 2.0)
            max_retries_per_key: Maximum retries per API key
        """
        if api_key:
            api_keys = [api_key]
        if not api_keys:
            raise ValueError("At least one OpenAI API key is required (use api_key or api_keys)")

        self._model = model
        self._temperature = temperature
        self.api_keys = cycle(api_keys)
        self._current_key = next(self.api_keys)
        self.max_retries = len(api_keys) * max_retries_per_key
        self._current_llm = self._create_llm()

    @property
    def model(self) -> str:
        """Get the model name."""
        return self._model

    @property
    def temperature(self) -> float:
        """Get the temperature setting."""
        return self._temperature

    @property
    def current_llm(self) -> ChatOpenAI:
        """Get the current LLM instance."""
        return self._current_llm

    @property
    def current_key(self) -> str:
        """Get the current API key being used."""
        return self._current_key

    def _create_llm(self) -> ChatOpenAI:
        """Create an instance of ChatOpenAI with the current API key."""
        return ChatOpenAI(
            model_name=self._model,
            temperature=self._temperature,
            openai_api_key=self._current_key,  # type: ignore[call-arg]
            max_retries=1,
        )

    def _rotate_key(self):
        """Rotate to the next API key in the list."""
        self._current_key = next(self.api_keys)
        logger.info(f"Rotating to new OpenAI API key: {self._current_key[:8]}...")
        self._current_llm = self._create_llm()

    def invoke(self, messages, **kwargs):
        """
        Invoke the OpenAI model with fault-tolerant API key rotation.

        Args:
            messages: Chat messages
            **kwargs: Additional arguments for the LLM

        Returns:
            LLM response

        Raises:
            Exception: If all API keys are exhausted
        """
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                return self._current_llm(messages=messages, **kwargs)
            except Exception as e:
                attempts += 1
                last_error = e
                logger.warning(
                    f"OpenAI API call failed (attempt {attempts}/{self.max_retries}): {str(e)}"
                )

                if attempts < self.max_retries:
                    self._rotate_key()
                    continue

                raise Exception(
                    f"All OpenAI API keys exhausted after {attempts} attempts. Last error: {str(last_error)}"
                ) from last_error


__all__ = ["OpenAI"]
