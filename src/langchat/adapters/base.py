# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Abstract base classes for LangChat adapters.

This module defines the adapter pattern interfaces that allow the library
to support multiple providers for LLM, vector stores, history storage, and reranking.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Implementations should provide methods for invoking language models
    with support for synchronous and asynchronous operations.
    """

    @property
    @abstractmethod
    def model(self) -> str:
        """Get the model name."""
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        """Get the temperature setting."""
        pass

    @property
    @abstractmethod
    def current_llm(self) -> Any:
        """
        Get the current LLM instance.
        
        This should return the underlying LangChain-compatible LLM object
        that can be used directly in chains.
        """
        pass

    @property
    @abstractmethod
    def current_key(self) -> Optional[str]:
        """
        Get the current API key being used.
        
        Returns None if no key is available or if the provider
        doesn't use API keys.
        """
        pass

    @abstractmethod
    def invoke(self, messages: Any, **kwargs: Any) -> Any:
        """
        Invoke the LLM synchronously.
        
        Args:
            messages: Chat messages (format depends on implementation)
            **kwargs: Additional arguments for the LLM
            
        Returns:
            LLM response
        """
        pass

    async def ainvoke(self, messages: Any, **kwargs: Any) -> Any:
        """
        Invoke the LLM asynchronously.
        
        Default implementation calls invoke in a thread pool.
        Implementations can override for better async performance.
        
        Args:
            messages: Chat messages (format depends on implementation)
            **kwargs: Additional arguments for the LLM
            
        Returns:
            LLM response
        """
        import asyncio
        return await asyncio.to_thread(self.invoke, messages, **kwargs)


class VectorStoreProvider(ABC):
    """
    Abstract base class for vector store providers.
    
    Implementations should provide methods for retrieving documents
    from vector databases.
    """

    @abstractmethod
    def get_retriever(self, k: int = 5) -> Any:
        """
        Get a retriever from the vector store.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            LangChain-compatible retriever instance
        """
        pass


class HistoryStore(ABC):
    """
    Abstract base class for history storage providers.
    
    Implementations should provide methods for storing and retrieving
    chat history and managing database operations.
    """

    @property
    @abstractmethod
    def client(self) -> Any:
        """
        Get the underlying client for database operations.
        
        The exact type depends on the implementation (e.g., Supabase Client).
        """
        pass

    @abstractmethod
    def check_tables_exist(self) -> bool:
        """
        Check if required database tables exist.
        
        Returns:
            True if tables exist and are accessible, False otherwise
        """
        pass

    @abstractmethod
    def get_create_tables_sql(self) -> str:
        """
        Get SQL statements needed to create required tables.
        
        Returns:
            SQL string with table creation statements
        """
        pass


class RerankerProvider(ABC):
    """
    Abstract base class for reranker providers.
    
    Implementations should provide methods for reranking retrieved documents
    to improve relevance.
    """

    @abstractmethod
    def create_compression_retriever(self, base_retriever: Any) -> Any:
        """
        Create a contextual compression retriever.
        
        Args:
            base_retriever: Base retriever to compress/rerank
            
        Returns:
            LangChain-compatible compression retriever instance
        """
        pass
