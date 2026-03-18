# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from langchat.adapters.logger import logger
from langchat.core.engine import LangChatEngine
from langchat.core.utils.document_indexer import DocumentIndexer
from langchat.types import ChatResponse


class LangChat:
    """Main entry point for the LangChat SDK.

    Combine any supported LLM, vector database, and history database to build
    a production-ready RAG chat application in a few lines of code.

    Args:
        llm: LLM platform instance (required).
        vector_db: Vector database adapter (required).
        db: Database adapter for chat-history storage (required).
        reranker: Reranker adapter (optional, defaults to Flashrank).
        prompt_template: Custom system-prompt template (optional).
        standalone_question_prompt: Custom standalone-question prompt (optional).
        verbose: Enable verbose debug logging (optional).
        max_chat_history: Number of past messages kept in context (default: 20).

    Examples::

        # Recommended — use langchat.platforms for automatic env-var loading
        from langchat import LangChat
        from langchat.platforms import OpenAI, Pinecone, Supabase

        lc = LangChat(
            llm=OpenAI("gpt-4o"),
            vector_db=Pinecone("my-index"),
            db=Supabase(),
        )

        # Async chat
        response = await lc.chat("What is RAG?", user_id="alice")
        print(response.text)

        # Sync chat (no asyncio boilerplate)
        response = lc.chat_sync("What is RAG?", user_id="alice")
        print(response.text)

        # Index documents
        lc.index("docs/guide.pdf")
        lc.index(["docs/guide.pdf", "docs/api.pdf"])
    """

    def __init__(
        self,
        *,
        llm=None,
        vector_db=None,
        db=None,
        reranker=None,
        prompt_template: str | None = None,
        standalone_question_prompt: str | None = None,
        verbose: bool | None = None,
        max_chat_history: int = 20,
    ):
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

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        query: str,
        user_id: str,
        platform: str = "default",
    ) -> ChatResponse:
        """Send a message and receive a typed response.

        Args:
            query: The user's message.
            user_id: Identifier for the user (used to isolate chat history).
            platform: Logical namespace for the conversation (default: ``"default"``).

        Returns:
            :class:`~langchat.types.ChatResponse` with ``.text``, ``.status``,
            ``.response_time``, and more.

        Examples::

            response = await lc.chat("Summarise the docs", user_id="alice")
            print(response.text)

            # Check success explicitly
            if response:
                print("OK:", response.text)
            else:
                print("Error:", response.error)
        """
        raw = await self.engine.chat(query=query, user_id=user_id, platform=platform)
        return ChatResponse(
            text=raw.get("response", ""),
            user_id=raw.get("user_id", user_id),
            platform=platform,
            status=raw.get("status", "error"),
            response_time=raw.get("response_time", 0.0),
            timestamp=raw.get("timestamp", ""),
            error=raw.get("error"),
        )

    def chat_sync(
        self,
        query: str,
        user_id: str,
        platform: str = "default",
    ) -> ChatResponse:
        """Synchronous version of :meth:`chat`. No ``asyncio`` boilerplate needed.

        Args:
            query: The user's message.
            user_id: Identifier for the user.
            platform: Logical namespace (default: ``"default"``).

        Returns:
            :class:`~langchat.types.ChatResponse`.

        Examples::

            response = lc.chat_sync("Hello", user_id="bob")
            print(response.text)
        """
        return asyncio.run(self.chat(query, user_id, platform))

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def get_session(self, user_id: str, platform: str = "default"):
        """Return (or create) the :class:`~langchat.core.session.UserSession`
        for this ``user_id`` / ``platform`` pair.

        Args:
            user_id: User identifier.
            platform: Logical namespace (default: ``"default"``).
        """
        return self.engine.get_session(user_id, platform)

    # ------------------------------------------------------------------
    # Document indexing
    # ------------------------------------------------------------------

    def index(
        self,
        paths: str | list[str],
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: str | None = None,
        prevent_duplicates: bool = True,
    ) -> dict:
        """Load and index one or more documents into the vector store.

        Accepts a single file path or a list of file paths.  Supported formats
        depend on the ``docsuite`` library (PDF, TXT, CSV, …).

        Duplicate detection is enabled by default — the same file will not be
        indexed twice even if you call ``index()`` multiple times.

        Args:
            paths: A file path (str) **or** a list of file paths.
            chunk_size: Token size of each text chunk (default: ``1000``).
            chunk_overlap: Overlap between consecutive chunks (default: ``200``).
            namespace: Pinecone namespace to store documents in (optional).
            prevent_duplicates: Skip chunks already present in the index
                (default: ``True``).

        Returns:
            dict with indexing statistics (``chunks_indexed``, ``chunks_skipped``, …).

        Examples::

            lc.index("docs/guide.pdf")
            lc.index(["docs/guide.pdf", "docs/api.pdf"])
            lc.index("docs/guide.pdf", namespace="v2", chunk_size=500)
        """
        indexer = self._build_indexer()

        if isinstance(paths, list):
            return indexer.load_and_index_multiple_documents(
                file_paths=paths,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                namespace=namespace,
                prevent_duplicates=prevent_duplicates,
            )

        return indexer.load_and_index_documents(
            file_path=paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            namespace=namespace,
            prevent_duplicates=prevent_duplicates,
        )

    # ------------------------------------------------------------------
    # Environment helpers
    # ------------------------------------------------------------------

    def load_env(self) -> None:
        """Load environment variables from a ``.env`` file in the working directory.

        Raises:
            FileNotFoundError: When ``.env`` does not exist.
        """
        if not Path(".env").exists():
            raise FileNotFoundError(
                ".env file not found. Create one or set environment variables directly."
            )
        load_dotenv()
        logger.info("Environment variables loaded from .env")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_indexer(self) -> DocumentIndexer:
        """Resolve credentials from the attached adapters and build a DocumentIndexer."""
        vector_adapter = getattr(self.engine, "vector_adapter", None)
        if vector_adapter is None:
            raise ValueError(
                "No vector_db adapter configured. Pass vector_db= when creating LangChat."
            )

        if not hasattr(vector_adapter, "api_key") or not hasattr(vector_adapter, "index_name"):
            raise ValueError("The vector_db adapter must expose api_key and index_name attributes.")

        embedding_api_key = self._resolve_embedding_key()

        return DocumentIndexer(
            pinecone_api_key=vector_adapter.api_key,
            pinecone_index_name=vector_adapter.index_name,
            openai_api_key=embedding_api_key,
            embedding_model=getattr(vector_adapter, "embedding_model", "text-embedding-3-large"),
        )

    def _resolve_embedding_key(self) -> str:
        """Extract the OpenAI API key from the configured LLM adapter."""
        llm = self.engine.llm

        if hasattr(llm, "api_keys") and llm.api_keys:
            key = getattr(llm, "_current_key", None)
            if key:
                return key

        if hasattr(llm, "current_llm") and hasattr(llm.current_llm, "api_key"):
            return llm.current_llm.api_key

        raise ValueError(
            "Could not resolve an OpenAI API key for embeddings from the LLM adapter. "
            "Ensure your LLM platform has API keys configured, or pass embedding_api_key "
            "directly to the Pinecone platform."
        )
