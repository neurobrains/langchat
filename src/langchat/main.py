"""
LangChat - Main entry point for developers.
This module provides an easy-to-use interface for creating conversational AI applications.
"""

import asyncio
from typing import List, Optional

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine
from langchat.logger import logger
from langchat.utils.document_indexer import DocumentIndexer


class LangChat:
    """
    Main LangChat class for developers.
    Easy to use and highly customizable.
    """

    def __init__(self, config: Optional[LangChatConfig] = None):
        """
        Initialize LangChat instance.

        Args:
            config: LangChat configuration. If None, creates config from environment variables.

        Example:
            ```python
            from langchat import LangChat, LangChatConfig

            # Create custom config
            config = LangChatConfig(
                openai_api_keys=["your-api-key"],
                pinecone_api_key="your-pinecone-key",
                supabase_url="your-supabase-url",
                supabase_key="your-supabase-key"
            )

            # Initialize LangChat
            langchat = LangChat(config=config)
            ```
        """
        if config is None:
            self.config = LangChatConfig.from_env()
        else:
            self.config = config
        self.engine = LangChatEngine(config=self.config)
        logger.info("LangChat initialized successfully")

    async def chat(self, query: str, user_id: str, domain: str = "default") -> dict:
        """
        Process a chat query.

        Args:
            query: User query text
            user_id: User ID
            domain: User domain (optional, defaults to "default")

        Returns:
            Dictionary with response and metadata

        Example:
            ```python
            result = await langchat.chat(
                query="What are the best universities in Europe?",
                user_id="user123",
                domain="education"
            )
            print(result["response"])
            ```
        """
        return await self.engine.chat(query=query, user_id=user_id, domain=domain)

    def chat_sync(self, query: str, user_id: str, domain: str = "default") -> dict:
        """
        Synchronous version of chat method.

        Args:
            query: User query text
            user_id: User ID
            domain: User domain (optional, defaults to "default")

        Returns:
            Dictionary with response and metadata

        Example:
            ```python
            result = langchat.chat_sync(
                query="What are the best universities in Europe?",
                user_id="user123"
            )
            print(result["response"])
            ```
        """
        return asyncio.run(self.chat(query, user_id, domain))

    def get_session(self, user_id: str, domain: str = "default"):
        """
        Get or create a user session.

        Args:
            user_id: User ID
            domain: User domain

        Returns:
            UserSession instance

        Example:
            ```python
            session = langchat.get_session(user_id="user123", domain="education")
            # Access session properties
            print(session.chat_history)
            ```
        """
        return self.engine.get_session(user_id, domain)

    def load_and_index_documents(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: Optional[str] = None,
        prevent_duplicates: bool = True,
    ) -> dict:
        """
        Load documents from a file, split them into chunks, and index them to Pinecone.

        This method uses docsuite to automatically detect and load various document types
        (PDF, TXT, CSV, etc.), splits them using LangChain's text splitter, and adds them
        to the Pinecone vectorstore using the existing configuration. Prevents duplicate
        documents from being indexed multiple times.

        Args:
            file_path: Path to the document file (supports PDF, TXT, CSV, etc.)
            chunk_size: Size of each text chunk (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            namespace: Optional Pinecone namespace to store documents in
            prevent_duplicates: If True, checks for existing documents before adding (default: True)

        Returns:
            Dictionary with indexing results including number of chunks indexed and skipped

        Example:
            ```python
            from langchat import LangChat, LangChatConfig

            config = LangChatConfig.from_env()
            langchat = LangChat(config=config)

            # Load and index a PDF document (prevents duplicates by default)
            result = langchat.load_and_index_documents(
                file_path="example.pdf",
                chunk_size=1000,
                chunk_overlap=200
            )
            print(f"Indexed {result['chunks_indexed']} chunks")
            print(f"Skipped {result.get('chunks_skipped', 0)} duplicate chunks")
            ```

        Raises:
            ValueError: If vector adapter is not initialized or config is missing
        """
        # Check if vector adapter is initialized
        if not hasattr(self.engine, "vector_adapter") or self.engine.vector_adapter is None:
            raise ValueError(
                "Vector adapter not initialized. Please ensure Pinecone API key and index name are configured."
            )

        # Check if required config values are available
        if not self.config.pinecone_api_key or not self.config.pinecone_index_name:
            raise ValueError("Pinecone API key and index name must be configured in LangChatConfig")

        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be configured in LangChatConfig")

        # Create DocumentIndexer instance using config values
        indexer = DocumentIndexer(
            pinecone_api_key=self.config.pinecone_api_key,
            pinecone_index_name=self.config.pinecone_index_name,
            openai_api_key=self.config.openai_api_keys[0],
            embedding_model=self.config.openai_embedding_model,
        )

        # Use DocumentIndexer to load and index documents
        return indexer.load_and_index_documents(
            file_path=file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
            prevent_duplicates=prevent_duplicates,
        )

    def load_and_index_multiple_documents(
        self,
        file_paths: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: Optional[str] = None,
        prevent_duplicates: bool = True,
    ) -> dict:
        """
        Load multiple documents, split them, and index them to Pinecone.

        Args:
            file_paths: List of file paths to load and index
            chunk_size: Size of each text chunk (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            namespace: Optional Pinecone namespace to store documents in
            prevent_duplicates: If True, checks for existing documents before adding (default: True)

        Returns:
            Dictionary with indexing results for all files

        Example:
            ```python
            result = langchat.load_and_index_multiple_documents(
                file_paths=["doc1.pdf", "doc2.txt", "data.csv"],
                chunk_size=1000,
                chunk_overlap=200
            )
            print(f"Total chunks indexed: {result['total_chunks_indexed']}")
            print(f"Total chunks skipped: {result.get('total_chunks_skipped', 0)}")
            ```
        """
        # Check if vector adapter is initialized
        if not hasattr(self.engine, "vector_adapter") or self.engine.vector_adapter is None:
            raise ValueError(
                "Vector adapter not initialized. Please ensure Pinecone API key and index name are configured."
            )

        # Check if required config values are available
        if not self.config.pinecone_api_key or not self.config.pinecone_index_name:
            raise ValueError("Pinecone API key and index name must be configured in LangChatConfig")

        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be configured in LangChatConfig")

        # Create DocumentIndexer instance using config values
        indexer = DocumentIndexer(
            pinecone_api_key=self.config.pinecone_api_key,
            pinecone_index_name=self.config.pinecone_index_name,
            openai_api_key=self.config.openai_api_keys[0],
            embedding_model=self.config.openai_embedding_model,
        )

        # Use DocumentIndexer to load and index multiple documents
        return indexer.load_and_index_multiple_documents(
            file_paths=file_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
            prevent_duplicates=prevent_duplicates,
        )
