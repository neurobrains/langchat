# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import asyncio
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from langchat.adapters.logger import logger
from langchat.core.engine import LangChatEngine
from langchat.core.utils.document_indexer import DocumentIndexer


class LangChat:
    """
    Main LangChat class for developers.
    Easy to use and highly customizable.
    """

    def __init__(
        self,
        *,
        llm=None,
        vector_db=None,
        db=None,
        reranker=None,
        prompt_template: Optional[str] = None,
        standalone_question_prompt: Optional[str] = None,
        verbose: Optional[bool] = None,
        max_chat_history: int = 20,
    ):
        """
        Initialize LangChat instance.

        Args:
            llm: LLM provider instance (required)
            vector_db: Vector database adapter (required)
            db: Database adapter for history storage (required)
            reranker: Reranker adapter (optional)
            prompt_template: System prompt template (optional)
            standalone_question_prompt: Standalone question prompt (optional)
            verbose: Enable verbose logging (optional)
            max_chat_history: Maximum chat history to keep (default: 20)

        Example:
            ```python
            from langchat import LangChat
            from langchat.adapters.llm import OpenAI
            from langchat.adapters.vector_db import Pinecone
            from langchat.adapters.database import Supabase

            # Initialize providers
            llm = OpenAI(api_keys=["sk-..."], model="gpt-4o-mini")
            vector_db = Pinecone(api_key="...", index_name="my-index", ...)
            db = Supabase.from_config(supabase_url="...", supabase_key="...")

            # Initialize LangChat
            langchat = LangChat(llm=llm, vector_db=vector_db, db=db)
            ```
        """
        self.engine = LangChatEngine(
            llm=llm,
            vector_db=vector_db,
            db=db,
            reranker=reranker,
            prompt_template=prompt_template,
            standalone_question_prompt=standalone_question_prompt,
            verbose=verbose,
            max_chat_history=max_chat_history,
        )
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
        """Synchronous version of chat method.

        Args:
            query: User query text
            user_id: User ID
            domain: User domain (optional, defaults to "default")

        Returns:
            dict: Dictionary with response and metadata
        """

        return asyncio.run(self.chat(query, user_id, domain))

    def get_session(self, user_id: str, domain: str = "default"):
        """Get or create a user session.

        Args:
            user_id: User ID
            domain: User domain (optional, defaults to "default")

        Returns:
            UserSession instance
        """

        return self.engine.get_session(user_id, domain)

    def load_env(self):
        """Load environment variables from .env file

        Raises:
            FileNotFoundError: Environment variables file not found
        """
        # Check if environment variables file exists
        if not Path(".env").exists():
            # Raise error if environment variables file not found
            raise FileNotFoundError("Environment variables file not found")
        else:
            # Load environment variables from .env file
            load_dotenv()
            # Log success message
            logger.info("Environment variables loaded successfully")

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
            from langchat import LangChat
            from langchat.adapters.llm import OpenAI
            from langchat.adapters.vector_db import Pinecone
            from langchat.adapters.database import Supabase

            llm = OpenAI(api_keys=["sk-..."], model="gpt-4o-mini")
            vector_db = Pinecone(api_key="...", index_name="my-index", ...)
            db = Supabase.from_config(supabase_url="...", supabase_key="...")
            langchat = LangChat(llm=llm, vector_db=vector_db, db=db)

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
            ValueError: If vector adapter is not initialized or required parameters are missing
        """
        # Check if vector adapter is initialized
        if not hasattr(self.engine, "vector_adapter") or self.engine.vector_adapter is None:
            raise ValueError(
                "Vector adapter not initialized. Please provide a vector_db adapter when initializing LangChat."
            )

        # Get required parameters from vector adapter
        vector_adapter = self.engine.vector_adapter
        if not hasattr(vector_adapter, "api_key") or not hasattr(vector_adapter, "index_name"):
            raise ValueError("Vector adapter must have api_key and index_name attributes")

        # Get embedding API key from LLM if available
        embedding_api_key = None
        if hasattr(self.engine.llm, "api_keys") and self.engine.llm.api_keys:
            embedding_api_key = self.engine.llm.api_keys[0]
        elif hasattr(self.engine.llm, "current_llm") and hasattr(
            self.engine.llm.current_llm, "api_key"
        ):
            embedding_api_key = self.engine.llm.current_llm.api_key

        # Check if embedding API key is available
        if embedding_api_key is None:
            raise ValueError(
                "Embedding API key is required for document indexing. "
                "Please ensure your LLM provider has API keys configured."
            )

        # Get embedding model from vector adapter
        embedding_model = getattr(vector_adapter, "embedding_model", "text-embedding-3-large")

        # Create DocumentIndexer instance
        indexer = DocumentIndexer(
            pinecone_api_key=vector_adapter.api_key,
            pinecone_index_name=vector_adapter.index_name,
            openai_api_key=embedding_api_key,
            embedding_model=embedding_model,
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
                "Vector adapter not initialized. Please provide a vector_db adapter when initializing LangChat."
            )

        # Get required parameters from vector adapter
        vector_adapter = self.engine.vector_adapter
        if not hasattr(vector_adapter, "api_key") or not hasattr(vector_adapter, "index_name"):
            raise ValueError("Vector adapter must have api_key and index_name attributes")

        # Get embedding API key from LLM if available
        embedding_api_key = None
        if hasattr(self.engine.llm, "api_keys") and self.engine.llm.api_keys:
            embedding_api_key = self.engine.llm.api_keys[0]
        elif hasattr(self.engine.llm, "current_llm") and hasattr(
            self.engine.llm.current_llm, "api_key"
        ):
            embedding_api_key = self.engine.llm.current_llm.api_key

        # Check if embedding API key is available
        if embedding_api_key is None:
            raise ValueError(
                "Embedding API key is required for document indexing. "
                "Please ensure your LLM provider has API keys configured."
            )

        # Get embedding model from vector adapter
        embedding_model = getattr(vector_adapter, "embedding_model", "text-embedding-3-large")

        # Create DocumentIndexer instance
        indexer = DocumentIndexer(
            pinecone_api_key=vector_adapter.api_key,
            pinecone_index_name=vector_adapter.index_name,
            openai_api_key=embedding_api_key,
            embedding_model=embedding_model,
        )

        # Use DocumentIndexer to load and index multiple documents
        return indexer.load_and_index_multiple_documents(
            file_paths=file_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
            prevent_duplicates=prevent_duplicates,
        )
