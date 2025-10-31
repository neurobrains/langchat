# Pinecone Vector Database Adapter

The Pinecone Adapter provides seamless integration with Pinecone vector database for semantic search and document retrieval.

## Overview

The `PineconeVectorAdapter` wraps Pinecone's vector database functionality, providing:

- **Vector Storage**: Store and retrieve document embeddings
- **Semantic Search**: Find similar documents using cosine similarity
- **Embedding Generation**: Automatic embedding generation with OpenAI
- **LangChain Integration**: Full compatibility with LangChain's retrieval chains

## Features

### 🔍 Semantic Search

Find similar documents based on meaning:
- Cosine similarity search
- Configurable result count
- Metadata filtering support

### 📊 Embedding Management

Automatic embedding generation:
- Uses OpenAI embeddings
- Supports multiple embedding models
- Efficient batch processing

### 🔗 LangChain Integration

Seamless integration with LangChain:
- Compatible with all LangChain retrieval chains
- Supports RAG (Retrieval-Augmented Generation)
- Works with rerankers

## Configuration

Configure through `LangChatConfig`:

```python
from langchat.config import LangChatConfig

config = LangChatConfig(
    pinecone_api_key="pcsk-...",
    pinecone_index_name="my-index",
    openai_embedding_model="text-embedding-3-large",
    retrieval_k=5  # Number of documents to retrieve
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pinecone_api_key` | `str` | Required | Pinecone API key |
| `pinecone_index_name` | `str` | Required | Name of the Pinecone index |
| `openai_embedding_model` | `str` | `"text-embedding-3-large"` | OpenAI embedding model |
| `openai_api_keys` | `List[str]` | Required | OpenAI API keys for embeddings |
| `retrieval_k` | `int` | `5` | Number of documents to retrieve |

## Usage

### Basic Usage

The adapter is automatically initialized by `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    pinecone_api_key="pcsk-...",
    pinecone_index_name="my-index",
    openai_api_keys=["sk-..."],
    # ... other config
)

langchat = LangChat(config=config)
# Adapter is automatically initialized
```

### Direct Usage (Advanced)

```python
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter

adapter = PineconeVectorAdapter(
    api_key="pcsk-...",
    index_name="my-index",
    embedding_model="text-embedding-3-large",
    embedding_api_key="sk-..."
)

# Get a retriever
retriever = adapter.get_retriever(k=10)
```

## API Reference

### Class: `PineconeVectorAdapter`

#### Constructor

```python
PineconeVectorAdapter(
    api_key: str,
    index_name: str,
    embedding_model: str = "text-embedding-3-large",
    embedding_api_key: Optional[str] = None
)
```

**Parameters:**
- `api_key` (str): Pinecone API key
- `index_name` (str): Name of the Pinecone index
- `embedding_model` (str): OpenAI embedding model name
- `embedding_api_key` (str, optional): OpenAI API key (uses Pinecone key if not provided)

#### Methods

##### `get_retriever(k: int = 5)`

Get a LangChain retriever from the vector store.

**Parameters:**
- `k` (int): Number of documents to retrieve (default: 5)

**Returns:**
- `Retriever`: LangChain retriever instance

**Example:**
```python
retriever = adapter.get_retriever(k=10)

# Use with LangChain chains
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

## How It Works

### Index Connection

```
1. Initialize Pinecone client with API key
2. Connect to specified index
3. Verify index is accessible
4. Initialize OpenAI embeddings
5. Create LangChain vector store wrapper
```

### Embedding Process

```
1. User query comes in
2. Generate embedding using OpenAI
3. Search Pinecone index using embedding
4. Return top K similar documents
5. Return to LangChain chain
```

## Pinecone Setup

### 1. Create Pinecone Account

1. Sign up at [pinecone.io](https://pinecone.io)
2. Create a new project
3. Get your API key

### 2. Create Index

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-api-key")

# Create index
pc.create_index(
    name="my-index",
    dimension=3072,  # For text-embedding-3-large
    metric="cosine"
)
```

### 3. Choose Embedding Dimension

Different OpenAI models have different dimensions:

| Model | Dimension |
|-------|-----------|
| `text-embedding-ada-002` | 1536 |
| `text-embedding-3-small` | 1536 |
| `text-embedding-3-large` | 3072 |

### 4. Populate Index

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# Add to Pinecone
PineconeVectorStore.from_documents(
    documents=docs,
    embedding=embeddings,
    index_name="my-index"
)
```

## Best Practices

### Index Naming

Use descriptive index names:
- `production-kb-v1`
- `staging-documents`
- `development-test`

### Embedding Models

Choose based on your needs:
- **Accuracy**: `text-embedding-3-large` (best quality)
- **Speed**: `text-embedding-3-small` (faster)
- **Balance**: `text-embedding-3-small` (recommended)

### Retrieval Count

Balance between relevance and context:
- **Fewer results (3-5)**: More focused, less context
- **More results (10-20)**: More context, may include noise

### Metadata Filtering

Use metadata for better retrieval:

```python
# Add metadata when upserting
vector_store.add_documents(
    documents=docs,
    metadatas=[
        {"source": "doc1", "category": "technical"},
        {"source": "doc2", "category": "general"}
    ]
)

# Filter during retrieval
retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"category": "technical"}
    }
)
```

## Troubleshooting

### Issue: Index Not Found

**Error:** `Index 'my-index' not found`

**Solution:**
- Check index name spelling
- Verify index exists in Pinecone console
- Check API key permissions

### Issue: Dimension Mismatch

**Error:** `Dimension mismatch: expected X, got Y`

**Solution:**
- Ensure embedding model dimension matches index dimension
- Recreate index with correct dimension if needed

### Issue: API Key Invalid

**Error:** `Invalid API key`

**Solution:**
- Verify API key format: should start with `pcsk-`
- Check key hasn't expired
- Ensure key has proper permissions

### Issue: Rate Limits

**Error:** `Rate limit exceeded`

**Solution:**
- Reduce request frequency
- Use Pinecone's free tier limits
- Upgrade to paid tier for higher limits

## Performance Optimization

### Batch Operations

For bulk operations, use batch processing:

```python
# Process in batches
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    vector_store.add_documents(batch)
```

### Index Optimization

- Use appropriate index type (serverless vs. pod)
- Monitor index usage
- Scale index based on load

### Caching

Cache frequently accessed queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str):
    return adapter.get_retriever().get_relevant_documents(query)
```

## Integration Examples

### Example 1: Basic Retrieval

```python
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter

adapter = PineconeVectorAdapter(
    api_key="pcsk-...",
    index_name="knowledge-base",
    embedding_model="text-embedding-3-large",
    embedding_api_key="sk-..."
)

retriever = adapter.get_retriever(k=5)
docs = retriever.get_relevant_documents("What is Python?")
```

### Example 2: With Reranking

```python
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter

# Base retriever
base_retriever = adapter.get_retriever(k=10)

# Add reranker
reranker = FlashrankRerankAdapter(top_n=5)
compression_retriever = reranker.create_compression_retriever(base_retriever)

# Use compressed retriever
docs = compression_retriever.get_relevant_documents("Python programming")
```

### Example 3: Custom Configuration

```python
config = LangChatConfig(
    pinecone_api_key="pcsk-...",
    pinecone_index_name="production-kb",
    openai_embedding_model="text-embedding-3-small",  # Faster model
    openai_api_keys=["sk-..."],
    retrieval_k=10  # Retrieve more for reranking
)
```

## Related Documentation

- [Configuration Guide](../configuration.md)
- [Flashrank Reranker](flashrank_adapter.md)
- [LangChat Engine](../core/engine.md)
- [Pinecone Documentation](https://docs.pinecone.io/)

