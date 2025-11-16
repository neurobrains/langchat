"""
OpenAI LLM service with API key rotation support.
"""

from itertools import cycle
from typing import List

from langchain_openai import ChatOpenAI

from langchat.logger import logger


class OpenAILLMService:
    """
    OpenAI LLM service with automatic API key rotation and retry logic.
    """

    def __init__(
        self,
        model: str,
        temperature: float,
        api_keys: List[str],
        max_retries_per_key: int = 2,
    ):
        """
        Initialize rotating OpenAI LLM service.

        Args:
            model: OpenAI model name (e.g., "gpt-4o-mini")
            temperature: Model temperature
            api_keys: List of OpenAI API keys for rotation
            max_retries_per_key: Maximum retries per API key
        """
        self.model = model
        self.temperature = temperature
        self.api_keys = cycle(api_keys) if api_keys else cycle([])
        self.current_key = next(self.api_keys) if api_keys else None
        self.max_retries = len(api_keys) * max_retries_per_key if api_keys else 0
        self.current_llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI:
        """
        Create an instance of ChatOpenAI with the current API key.
        """
        if not self.current_key:
            raise ValueError("No API keys provided")

        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            openai_api_key=self.current_key,  # type: ignore[call-arg]
            max_retries=1,
        )

    def _rotate_key(self):
        """
        Rotate to the next API key in the list.
        """
        self.current_key = next(self.api_keys)
        logger.info(f"Rotating to new API key: {self.current_key[:8]}...")
        self.current_llm = self._create_llm()

    def invoke(self, messages, **kwargs):
        """
        Invoke the ChatOpenAI model with fault-tolerant API key rotation.

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
                # Make the API call
                return self.current_llm(messages=messages, **kwargs)
            except Exception as e:
                attempts += 1
                last_error = e
                logger.warning(f"API call failed (attempt {attempts}/{self.max_retries}): {str(e)}")

                # Rotate to next key and retry
                if attempts < self.max_retries:
                    self._rotate_key()
                    continue

                raise Exception(
                    f"All API keys exhausted after {attempts} attempts. Last error: {str(last_error)}"
                ) from last_error
