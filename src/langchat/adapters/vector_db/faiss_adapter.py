# Copyright (c) 2026 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from langchat.adapters.base import VectorStoreProvider
from langchat.adapters.logger import logger


class FAISSVectorAdapter(VectorStoreProvider):
    """
    Adapter for FAISS local vector store — no external API required.

    The index is persisted to ``index_path`` so it survives restarts.
    If the path does not exist yet, an empty index is created automatically.
    """

    def __init__(
        self,
        index_path: str = "faiss_index",
        embedding_model: str = "text-embedding-3-large",
        embedding_api_key: str | None = None,
    ):
        """
        Initialize FAISS vector adapter.

        Args:
            index_path: Directory where the FAISS index files are saved/loaded.
            embedding_model: OpenAI embedding model name.
            embedding_api_key: OpenAI API key for embeddings
                               (falls back to ``OPENAI_API_KEY`` env var).
        """
        self.index_path = index_path
        self.embedding_model = embedding_model
        self.embedding_api_key = embedding_api_key or os.getenv("OPENAI_API_KEY")

        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=self.embedding_api_key,  # type: ignore[call-arg]
        )

        if Path(index_path).exists():
            self.vector_store = FAISS.load_local(
                index_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info(f"Loaded existing FAISS index from '{index_path}'")
        else:
            # Bootstrap with a placeholder so the store is usable immediately
            self.vector_store = FAISS.from_texts(["init"], self.embeddings)
            self.vector_store.save_local(index_path)
            logger.info(f"Created new FAISS index at '{index_path}'")

    def get_retriever(self, k: int = 5):
        """
        Return a retriever over the local FAISS index.

        Args:
            k: Number of documents to retrieve.

        Returns:
            Retriever instance.
        """
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def save(self) -> None:
        """Persist the current index to ``index_path``."""
        self.vector_store.save_local(self.index_path)
        logger.info(f"FAISS index saved to '{self.index_path}'")
