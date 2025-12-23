# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""RAG Agent - Retrieval Augmented Generation agent."""

from __future__ import annotations

import asyncio
from typing import Any

from langchat.adapters.logger import logger
from langchat.core.prompts import generate_standalone_question
from langchat.core.session import UserSession
from langchat.database.id_manager import IDManager


class RAGAgent:
    """
    RAG (Retrieval Augmented Generation) Agent.

    Combines vector search, reranking, and LLM generation with chat history
    to provide contextual, accurate responses.

    Example:
        ```python
        from langchat import RAGAgent
        from langchat.providers import OpenAIProvider, PineconeProvider

        # Create RAG agent
        agent = RAGAgent(
            llm=OpenAIProvider(api_keys=["sk-..."], model="gpt-4o-mini"),
            vector_db=PineconeProvider(
                api_key="...",
                index_name="my-index",
                embedding_model="text-embedding-3-large",
                embedding_api_key="sk-..."
            ),
            db=SupabaseProvider.from_config(url="...", key="...")
        )

        # Chat with the agent
        response = await agent.chat("What is machine learning?", user_id="user123")
        print(response["response"])
        ```
    """

    def __init__(
        self,
        llm: Any = None,
        vector_db: Any = None,
        db: Any = None,
        reranker: Any = None,
        prompt_template: str | None = None,
        standalone_question_prompt: str | None = None,
        verbose: bool = False,
        max_chat_history: int = 20,
    ):
        """
        Initialize RAG agent.

        Args:
            llm: LLM provider instance (REQUIRED, e.g., OpenAI, Gemini, Anthropic)
            vector_db: Vector database provider (REQUIRED, e.g., Pinecone)
            db: Database provider for chat history (REQUIRED, e.g., Supabase)
            reranker: Reranker provider (REQUIRED, e.g., Flashrank)
            prompt_template: Custom prompt template
            standalone_question_prompt: Custom standalone question prompt
            verbose: Enable verbose logging
            max_chat_history: Maximum number of chat messages to keep in history
        """
        # Validate required providers
        if not all([llm, vector_db, db, reranker]):
            self.llm = llm
            self.vector_db = vector_db
            self.db = db
            self.reranker = reranker

        # Internal state
        self.sessions: dict[str, UserSession] = {}
        self.id_manager = IDManager(self.db.client)

        # Configuration
        self.prompt_template = prompt_template
        self.standalone_question_prompt = standalone_question_prompt
        self.verbose = verbose
        self.max_chat_history = max_chat_history

        logger.info("RAG Agent initialized successfully")

    def get_session(self, user_id: str, domain: str = "default") -> UserSession:
        """
        Get or create a user session.

        Args:
            user_id: User ID
            domain: User domain/namespace

        Returns:
            UserSession instance
        """
        session_key = f"{user_id}_{domain}"

        if session_key not in self.sessions:
            self.sessions[session_key] = UserSession(
                domain=domain,
                user_id=user_id,
                llm=self.llm,
                vector_adapter=self.vector_db,
                reranker_adapter=self.reranker,
                history_store=self.db,
                id_manager=self.id_manager,
                prompt_template=self.prompt_template,
                memory_window=20,
                max_chat_history=self.max_chat_history,
                retrieval_k=5,
            )

        return self.sessions[session_key]

    async def chat(
        self,
        query: str,
        user_id: str,
        domain: str = "default",
        standalone_question: str | None = None,
        return_sources: bool = False,
    ) -> dict[str, Any]:
        """
        Process a chat query with RAG.

        Args:
            query: User query
            user_id: User ID
            domain: User domain
            standalone_question: Optional pre-generated standalone question
            return_sources: Include source documents in response

        Returns:
            Dictionary with response and metadata
        """
        try:
            session = self.get_session(user_id, domain)

            # Generate standalone question if needed
            if not standalone_question:
                try:
                    standalone_question = await generate_standalone_question(
                        query=query,
                        chat_history=session.chat_history,
                        custom_prompt=self.standalone_question_prompt,
                        verbose_chains=self.verbose,
                        llm=self.llm,
                    )
                    if self.verbose:
                        logger.info(f"Standalone question: {standalone_question}")
                except Exception as e:
                    logger.warning(f"Error generating standalone question: {e}")
                    standalone_question = query

            # Process conversation
            result = await session.conversation.ainvoke(
                {"query": query, "standalone_question": standalone_question}
            )

            # Extract response
            response_text = result.get("output_text") or result.get("answer", "")

            # Update chat history
            session.chat_history.append((query, response_text))
            if len(session.chat_history) > self.max_chat_history:
                excess = len(session.chat_history) - self.max_chat_history
                del session.chat_history[:excess]

            # Save message in background
            asyncio.create_task(self._save_message_async(session, query, response_text))

            response_data = {
                "response": response_text,
                "user_id": user_id,
                "domain": domain,
                "status": "success",
            }

            if return_sources and "source_documents" in result:
                response_data["sources"] = [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                    for doc in result["source_documents"]
                ]

            return response_data

        except Exception as e:
            logger.error(f"Error in RAG chat: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your request.",
                "user_id": user_id,
                "domain": domain,
                "status": "error",
                "error": str(e),
            }

    def chat_sync(
        self,
        query: str,
        user_id: str,
        domain: str = "default",
        return_sources: bool = False,
    ) -> dict[str, Any]:
        """
        Synchronous version of chat method.

        Args:
            query: User query
            user_id: User ID
            domain: User domain
            return_sources: Include source documents in response

        Returns:
            Dictionary with response and metadata
        """
        return asyncio.run(self.chat(query, user_id, domain, return_sources=return_sources))

    async def _save_message_async(self, session: UserSession, query: str, response: str):
        """Save message to database asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, session.save_message, query, response)
        except Exception as e:
            logger.error(f"Error saving message: {e}")

    def load_documents(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: str | None = None,
        pinecone_api_key: str | None = None,
        embedding_api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Load and index documents into the vector database.

        Args:
            file_path: Path to document file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            namespace: Optional namespace for documents
            pinecone_api_key: Pinecone API key (uses vector_db config if not provided)
            embedding_api_key: OpenAI API key for embeddings (uses vector_db config if not provided)

        Returns:
            Dictionary with indexing results
        """
        from langchat.core.utils.document_indexer import DocumentIndexer

        # Get config from vector_db adapter
        pinecone_api_key = pinecone_api_key or getattr(self.vector_db, 'api_key', None)
        index_name = getattr(self.vector_db, 'index_name', None)
        embedding_api_key = embedding_api_key or getattr(self.vector_db, 'embedding_api_key', None)
        embedding_model = getattr(self.vector_db, 'embedding_model', 'text-embedding-3-large')

        if not pinecone_api_key or not index_name:
            raise ValueError("Pinecone API key and index name must be configured in vector_db")

        if not embedding_api_key:
            raise ValueError("OpenAI API key must be configured for embeddings")

        indexer = DocumentIndexer(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=index_name,
            openai_api_key=embedding_api_key,
            embedding_model=embedding_model,
        )

        return indexer.load_and_index_documents(
            file_path=file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
        )

    def load_multiple_documents(
        self,
        file_paths: list[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: str | None = None,
        pinecone_api_key: str | None = None,
        embedding_api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Load and index multiple documents.

        Args:
            file_paths: List of file paths
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            namespace: Optional namespace for documents
            pinecone_api_key: Pinecone API key (uses vector_db config if not provided)
            embedding_api_key: OpenAI API key for embeddings (uses vector_db config if not provided)

        Returns:
            Dictionary with indexing results
        """
        from langchat.core.utils.document_indexer import DocumentIndexer

        # Get config from vector_db adapter
        pinecone_api_key = pinecone_api_key or getattr(self.vector_db, 'api_key', None)
        index_name = getattr(self.vector_db, 'index_name', None)
        embedding_api_key = embedding_api_key or getattr(self.vector_db, 'embedding_api_key', None)
        embedding_model = getattr(self.vector_db, 'embedding_model', 'text-embedding-3-large')

        if not pinecone_api_key or not index_name:
            raise ValueError("Pinecone API key and index name must be configured in vector_db")

        if not embedding_api_key:
            raise ValueError("OpenAI API key must be configured for embeddings")

        indexer = DocumentIndexer(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=index_name,
            openai_api_key=embedding_api_key,
            embedding_model=embedding_model,
        )

        return indexer.load_and_index_multiple_documents(
            file_paths=file_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
        )


__all__ = ["RAGAgent"]

