"""
Standalone document loader and indexer for Pinecone.
This module provides a simple interface to load documents and index them to Pinecone
without requiring the full LangChat configuration.
"""

import hashlib
import os
import uuid
from typing import Dict, List, Optional

from docsuite import UnifiedDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from pinecone import Pinecone

from langchat.exceptions import UnsupportedFileTypeError
from langchat.logger import logger


class DocumentIndexer:
    """
    Standalone document loader and indexer for Pinecone.
    Only requires Pinecone API key and OpenAI API key for embeddings.
    """

    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_index_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-large",
    ):
        """
        Initialize DocumentIndexer.

        Args:
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Name of the Pinecone index
            openai_api_key: OpenAI API key for generating embeddings
            embedding_model: OpenAI embedding model name (default: "text-embedding-3-large")

        Example:
            ```python
            from langchat.utils.document_indexer import DocumentIndexer

            indexer = DocumentIndexer(
                pinecone_api_key="your-pinecone-key",
                pinecone_index_name="your-index",
                openai_api_key="your-openai-key"
            )
            ```
        """
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.openai_api_key = openai_api_key
        self.embedding_model = embedding_model

        # Set environment variable for Pinecone
        os.environ["PINECONE_API_KEY"] = pinecone_api_key

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(pinecone_index_name)

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=openai_api_key,  # type: ignore[call-arg]
        )

        # Initialize vector store
        self.vector_store = PineconeVectorStore(index=self.index, embedding=self.embeddings)

        # Verify index is accessible and get dimension
        try:
            # Get dimension from index stats (if available) or use default
            # For OpenAI embeddings, dimensions are typically 1536 (ada-002) or 3072 (text-embedding-3-large)
            # We'll determine it from the embedding model
            if "text-embedding-3-large" in embedding_model:
                self.embedding_dimension = 3072
            elif "text-embedding-3-small" in embedding_model:
                self.embedding_dimension = 1536
            else:
                # Default to 1536 for older models
                self.embedding_dimension = 1536
            self.index.describe_index_stats()
            logger.info(f"Successfully connected to Pinecone index: {pinecone_index_name}")
        except Exception as e:
            logger.error(f"Error connecting to Pinecone index: {str(e)}")
            raise RuntimeError(f"Error connecting to Pinecone: {str(e)}") from e

    def _generate_document_hash(self, file_path: str, chunk_content: str) -> str:
        """
        Generate a unique hash for a document chunk based on file path and content.

        Args:
            file_path: Path to the document file
            chunk_content: Content of the chunk

        Returns:
            SHA256 hash string
        """
        # Create a unique identifier based on file path and content
        content = f"{file_path}:{chunk_content}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _check_chunk_exists(self, chunk_hash: str, namespace: Optional[str] = None) -> bool:
        """
        Check if a chunk with the given hash already exists in Pinecone.

        Args:
            chunk_hash: Hash of the chunk to check
            namespace: Optional namespace to check in

        Returns:
            True if chunk exists, False otherwise
        """
        try:
            # Query for the hash in metadata using a dummy vector
            # We use the embedding dimension we determined during initialization
            dummy_vector = [0.0] * self.embedding_dimension
            results = self.index.query(
                vector=dummy_vector,
                top_k=1,
                filter={"document_hash": {"$eq": chunk_hash}},
                namespace=namespace,
                include_metadata=True,
            )
            return len(results.matches) > 0
        except Exception as e:
            logger.warning(f"Error checking for existing chunk: {str(e)}")
            # If query fails, assume chunk doesn't exist to be safe
            return False

    def load_and_index_documents(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: Optional[str] = None,
        prevent_duplicates: bool = True,
    ) -> Dict:
        """
        Load documents from a file, split them into chunks, and index them to Pinecone.

        This method uses docsuite to automatically detect and load various document types
        (PDF, TXT, CSV, etc.), splits them using LangChain's text splitter, and adds them
        to the Pinecone vectorstore. Optionally prevents duplicate documents.

        Args:
            file_path: Path to the document file (supports PDF, TXT, CSV, etc.)
            chunk_size: Size of each text chunk (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            namespace: Optional Pinecone namespace to store documents in
            prevent_duplicates: If True, checks for existing documents before adding (default: True)

        Returns:
            Dictionary with indexing results including number of chunks indexed

        Example:
            ```python
            from langchat.utils.document_indexer import DocumentIndexer

            indexer = DocumentIndexer(
                pinecone_api_key="your-pinecone-key",
                pinecone_index_name="your-index",
                openai_api_key="your-openai-key"
            )

            # Load and index a PDF document
            result = indexer.load_and_index_documents(
                file_path="example.pdf",
                chunk_size=1000,
                chunk_overlap=200
            )
            print(f"Indexed {result['chunks_indexed']} chunks")
            print(f"Skipped {result['chunks_skipped']} duplicate chunks")
            ```

        Raises:
            UnsupportedFileTypeError: If the file type is not supported by docsuite
            RuntimeError: If indexing fails
        """
        logger.info(f"Loading document from: {file_path}")

        # Load document using docsuite
        try:
            loader = UnifiedDocumentLoader(file_path)
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} document(s) from {file_path}")
        except UnsupportedFileTypeError as e:
            logger.error(f"Unsupported file type: {str(e)}")
            raise
        except Exception as e:
            # Check if the error is related to unsupported file types
            error_msg = str(e).lower()
            if any(
                keyword in error_msg
                for keyword in ["unsupported", "file type", "format not supported", "cannot load"]
            ):
                logger.error(f"Unsupported file type: {str(e)}")
                raise UnsupportedFileTypeError(f"File type not supported: {str(e)}") from e
            logger.error(f"Error loading document: {str(e)}")
            raise

        if not documents:
            logger.warning(f"No documents loaded from {file_path}")
            return {
                "status": "success",
                "chunks_indexed": 0,
                "chunks_skipped": 0,
                "message": "No documents to index",
            }

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        logger.info(
            f"Splitting documents into chunks (size: {chunk_size}, overlap: {chunk_overlap})"
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} document(s)")

        # Filter out duplicates if prevent_duplicates is enabled
        chunks_to_index = []
        chunks_skipped = 0

        if prevent_duplicates:
            logger.info("Checking for duplicate chunks...")
            for chunk in chunks:
                chunk_hash = self._generate_document_hash(file_path, chunk.page_content)

                # Add hash to metadata for future duplicate detection
                if not chunk.metadata:
                    chunk.metadata = {}
                chunk.metadata["document_hash"] = chunk_hash
                chunk.metadata["source_file"] = file_path

                # Check if chunk already exists
                if self._check_chunk_exists(chunk_hash, namespace):
                    chunks_skipped += 1
                    logger.debug(f"Skipping duplicate chunk (hash: {chunk_hash[:8]}...)")
                else:
                    chunks_to_index.append(chunk)

            logger.info(
                f"Found {chunks_skipped} duplicate chunks, {len(chunks_to_index)} new chunks to index"
            )
        else:
            # Add metadata without duplicate checking
            for chunk in chunks:
                if not chunk.metadata:
                    chunk.metadata = {}
                chunk.metadata["source_file"] = file_path
            chunks_to_index = chunks

        if not chunks_to_index:
            logger.info("No new chunks to index (all are duplicates)")
            return {
                "status": "success",
                "chunks_indexed": 0,
                "chunks_skipped": chunks_skipped,
                "documents_loaded": len(documents),
                "file_path": file_path,
                "namespace": namespace,
                "message": "All chunks were duplicates, nothing indexed",
            }

        # Index chunks to Pinecone
        try:
            # Generate unique IDs for each chunk
            chunk_ids = [str(uuid.uuid4()) for _ in chunks_to_index]

            # Add IDs to chunk metadatas
            for i, chunk in enumerate(chunks_to_index):
                chunk.metadata["chunk_id"] = chunk_ids[i]

            # Add documents to vector store
            if namespace:
                # Use direct index upsert for namespace support
                logger.info(f"Indexing to namespace: {namespace}")
                texts = [chunk.page_content for chunk in chunks_to_index]
                metadatas = [chunk.metadata for chunk in chunks_to_index]

                # Generate embeddings
                embeddings = self.embeddings.embed_documents(texts)

                # Add to Pinecone with namespace
                self.index.upsert(
                    vectors=[
                        {
                            "id": chunk_ids[i],
                            "values": embeddings[i],
                            "metadata": metadatas[i] if metadatas[i] else {},
                        }
                        for i in range(len(chunks_to_index))
                    ],
                    namespace=namespace,
                )
            else:
                # Use standard add_documents method
                try:
                    # Try with ids parameter (if supported)
                    self.vector_store.add_documents(chunks_to_index, ids=chunk_ids)
                except TypeError:
                    # If ids parameter is not supported, use without it
                    self.vector_store.add_documents(chunks_to_index)

            logger.info(f"Successfully indexed {len(chunks_to_index)} chunks to Pinecone")

            return {
                "status": "success",
                "chunks_indexed": len(chunks_to_index),
                "chunks_skipped": chunks_skipped,
                "documents_loaded": len(documents),
                "file_path": file_path,
                "namespace": namespace,
            }

        except Exception as e:
            logger.error(f"Error indexing documents to Pinecone: {str(e)}")
            raise RuntimeError(f"Failed to index documents: {str(e)}") from e

    def load_and_index_multiple_documents(
        self,
        file_paths: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        namespace: Optional[str] = None,
        prevent_duplicates: bool = True,
    ) -> Dict:
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
            result = indexer.load_and_index_multiple_documents(
                file_paths=["doc1.pdf", "doc2.txt", "data.csv"],
                chunk_size=1000,
                chunk_overlap=200
            )
            print(f"Total chunks indexed: {result['total_chunks_indexed']}")
            ```
        """
        total_chunks = 0
        total_skipped = 0
        results = []
        errors = []

        for file_path in file_paths:
            try:
                result = self.load_and_index_documents(
                    file_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    namespace=namespace,
                    prevent_duplicates=prevent_duplicates,
                )
                total_chunks += result["chunks_indexed"]
                total_skipped += result.get("chunks_skipped", 0)
                results.append({"file_path": file_path, "status": "success", **result})
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing {file_path}: {error_msg}")
                errors.append({"file_path": file_path, "error": error_msg})
                results.append({"file_path": file_path, "status": "error", "error": error_msg})

        return {
            "status": "completed",
            "total_chunks_indexed": total_chunks,
            "total_chunks_skipped": total_skipped,
            "files_processed": len(file_paths),
            "files_succeeded": len([r for r in results if r.get("status") == "success"]),
            "files_failed": len(errors),
            "results": results,
            "errors": errors if errors else None,
        }
