# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""RAG Agent - Retrieval Augmented Generation agent."""

from __future__ import annotations

import asyncio
from typing import Any

from langchat.adapters.db.utils.id_manager import IDManager
from langchat.adapters.logger import logger
from langchat.core.config import LangChatConfig
from langchat.core.prompts import generate_standalone_question
from langchat.core.session import UserSession
from langchat.providers import (
    create_database_provider,
    create_llm_provider,
    create_reranker_provider,
    create_vector_db_provider,
)


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
        config: LangChatConfig | None = None,
        prompt_template: str | None = None,
        standalone_question_prompt: str | None = None,
        verbose: bool = False,
    ):
        """
        Initialize RAG agent.

        Args:
            llm: LLM provider instance (e.g., OpenAIProvider, GeminiProvider)
            vector_db: Vector database provider (e.g., PineconeProvider)
            db: Database provider for chat history (e.g., SupabaseProvider)
            reranker: Reranker provider (e.g., FlashrankProvider)
            config: LangChatConfig instance (used if providers not specified)
            prompt_template: Custom prompt template
            standalone_question_prompt: Custom standalone question prompt
            verbose: Enable verbose logging
        """
        self.config = config or LangChatConfig.from_env()

        # Initialize providers
        self.llm = llm or create_llm_provider("auto", self.config)
        self.vector_db = vector_db or create_vector_db_provider("pinecone", self.config)
        self.db = db or create_database_provider("supabase", self.config)
        self.reranker = reranker or create_reranker_provider("flashrank", self.config)

        # Internal state
        self.sessions: dict[str, UserSession] = {}
        self.id_manager = IDManager(self.db.client)

        # Configuration
        self.prompt_template = (
            prompt_template
            or self.config.system_prompt_template
            or self.config.get_default_prompt_template()
        )
        self.standalone_question_prompt = (
            standalone_question_prompt or self.config.standalone_question_prompt
        )
        self.verbose = verbose
        self.max_chat_history = self.config.max_chat_history

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
                config=self.config,
                llm=self.llm,
                vector_adapter=self.vector_db,
                reranker_adapter=self.reranker,
                history_store=self.db,
                id_manager=self.id_manager,
                prompt_template=self.prompt_template,
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
    ) -> dict[str, Any]:
        """
        Load and index documents into the vector database.

        Args:
            file_path: Path to document file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            namespace: Optional namespace for documents

        Returns:
            Dictionary with indexing results
        """
        from langchat.core.utils.document_indexer import DocumentIndexer

        # Validate required config values
        if not self.config.pinecone_api_key or not self.config.pinecone_index_name:
            raise ValueError("Pinecone API key and index name must be configured")
        
        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be configured for embeddings")

        indexer = DocumentIndexer(
            pinecone_api_key=self.config.pinecone_api_key,
            pinecone_index_name=self.config.pinecone_index_name,
            openai_api_key=self.config.openai_api_keys[0],
            embedding_model=self.config.openai_embedding_model,
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
    ) -> dict[str, Any]:
        """
        Load and index multiple documents.

        Args:
            file_paths: List of file paths
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            namespace: Optional namespace for documents

        Returns:
            Dictionary with indexing results
        """
        from langchat.core.utils.document_indexer import DocumentIndexer

        # Validate required config values
        if not self.config.pinecone_api_key or not self.config.pinecone_index_name:
            raise ValueError("Pinecone API key and index name must be configured")
        
        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be configured for embeddings")

        indexer = DocumentIndexer(
            pinecone_api_key=self.config.pinecone_api_key,
            pinecone_index_name=self.config.pinecone_index_name,
            openai_api_key=self.config.openai_api_keys[0],
            embedding_model=self.config.openai_embedding_model,
        )

        return indexer.load_and_index_multiple_documents(
            file_paths=file_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
        )


__all__ = ["RAGAgent"]

