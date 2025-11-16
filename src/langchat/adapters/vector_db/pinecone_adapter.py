"""
Pinecone vector database adapter.
"""

import os
from typing import Optional

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from pinecone import Pinecone

from langchat.logger import logger


class PineconeVectorAdapter:
    """
    Adapter for Pinecone vector database operations.
    """

    def __init__(
        self,
        api_key: str,
        index_name: str,
        embedding_model: str = "text-embedding-3-large",
        embedding_api_key: Optional[str] = None,
    ):
        """
        Initialize Pinecone vector adapter.

        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            embedding_model: OpenAI embedding model name
            embedding_api_key: OpenAI API key for embeddings (uses Pinecone key if not provided)
        """
        self.api_key = api_key
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.embedding_api_key = embedding_api_key

        # Set environment variable for Pinecone
        os.environ["PINECONE_API_KEY"] = api_key

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=embedding_api_key,  # type: ignore[call-arg]
        )

        # Initialize vector store
        self.vector_store = PineconeVectorStore(index=self.index, embedding=self.embeddings)

        # Verify index is accessible
        try:
            self.index.describe_index_stats()
            logger.info(f"Successfully connected to Pinecone index: {index_name}")
        except Exception as e:
            logger.error(f"Error connecting to Pinecone index: {str(e)}")
            raise RuntimeError(f"Error loading Pinecone: {str(e)}") from e

    def get_retriever(self, k: int = 5):
        """
        Get a retriever from the vector store.

        Args:
            k: Number of documents to retrieve

        Returns:
            Retriever instance
        """
        return self.vector_store.as_retriever(search_kwargs={"k": k})
