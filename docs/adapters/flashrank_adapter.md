# Flashrank Reranker Adapter

The Flashrank Reranker Adapter provides document reranking using Flashrank models to improve retrieval quality.

## Overview

The `FlashrankRerankAdapter` implements reranking functionality that:

- **Improves Relevance**: Re-ranks retrieved documents for better relevance
- **Fast Performance**: Uses optimized ONNX models for speed
- **Easy Integration**: Seamlessly integrates with LangChain retrieval chains
- **Automatic Model Download**: Downloads models automatically on first use

## Features

### 🎯 Improved Retrieval Quality

Rerank retrieved documents to improve relevance:
- Better top-K results
- Improved context for LLM
- Higher accuracy in RAG systems

### ⚡ High Performance

Optimized for speed:
- ONNX-based models
- Local inference (no API calls)
- Fast batch processing

### 📦 Automatic Model Management

Models downloaded and cached automatically:
- First-time download
- Local caching
- Configurable cache directory

## Configuration

Configure through `LangChatConfig`:

```python
from langchat.config import LangChatConfig

config = LangChatConfig(
    reranker_model="ms-marco-MiniLM-L-12-v2",
    reranker_cache_dir="rerank_models",
    reranker_top_n=3  # Top documents after reranking
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reranker_model` | `str` | `"ms-marco-MiniLM-L-12-v2"` | Flashrank model name |
| `reranker_cache_dir` | `str` | `"rerank_models"` | Directory to cache models |
| `reranker_top_n` | `int` | `3` | Number of top documents after reranking |

## Usage

### Basic Usage

The adapter is automatically initialized by `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    reranker_model="ms-marco-MiniLM-L-12-v2",
    reranker_cache_dir="rerank_models",
    reranker_top_n=3,
    # ... other config
)

langchat = LangChat(config=config)
# Adapter is automatically initialized and used in retrieval
```

### Direct Usage (Advanced)

```python
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter

# Create base retriever
vector_adapter = PineconeVectorAdapter(...)
base_retriever = vector_adapter.get_retriever(k=10)

# Create reranker
reranker = FlashrankRerankAdapter(
    model_name="ms-marco-MiniLM-L-12-v2",
    cache_dir="rerank_models",
    top_n=5
)

# Create compression retriever (reranks results)
compression_retriever = reranker.create_compression_retriever(base_retriever)

# Use with LangChain
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=compression_retriever  # Uses reranked results
)
```

## API Reference

### Class: `FlashrankRerankAdapter`

#### Constructor

```python
FlashrankRerankAdapter(
    model_name: str = "ms-marco-MiniLM-L-12-v2",
    cache_dir: str = "rerank_models",
    top_n: int = 3
)
```

**Parameters:**
- `model_name` (str): Flashrank model name (default: "ms-marco-MiniLM-L-12-v2")
- `cache_dir` (str): Directory to cache the model (default: "rerank_models")
- `top_n` (int): Number of top documents after reranking (default: 3)

#### Methods

##### `create_compression_retriever(base_retriever)`

Create a contextual compression retriever that reranks documents.

**Parameters:**
- `base_retriever`: Base retriever to compress (from vector database)

**Returns:**
- `ContextualCompressionRetriever`: Retriever with reranking

**Example:**
```python
base_retriever = vector_adapter.get_retriever(k=10)
compression_retriever = reranker.create_compression_retriever(base_retriever)

# Use in retrieval chain
docs = compression_retriever.get_relevant_documents(query)
```

## How It Works

### Reranking Pipeline

```
1. Retrieve documents from vector store (k=10)
   ↓
2. Pass documents + query to reranker
   ↓
3. Rerank based on relevance scores
   ↓
4. Return top N documents (top_n=3)
   ↓
5. Use reranked documents in LLM context
```

### Model Initialization

```
1. Check if model exists in cache_dir
2. If not, download model automatically
3. Initialize Flashrank Ranker
4. Wrap in LangChain FlashrankRerank
5. Ready for use
```

## Available Models

Flashrank provides several pre-trained models:

### Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|--------|----------|
| `ms-marco-MiniLM-L-12-v2` | Small | Fast | Good | **Recommended** |
| `ms-marco-MiniLM-L-6-v2` | Small | Very Fast | Good | Speed priority |
| `rank-T5-flan` | Large | Slow | Excellent | Quality priority |

### Model Selection

```python
# Balanced (Recommended)
reranker = FlashrankRerankAdapter(
    model_name="ms-marco-MiniLM-L-12-v2",
    top_n=5
)

# Speed Priority
reranker = FlashrankRerankAdapter(
    model_name="ms-marco-MiniLM-L-6-v2",
    top_n=5
)

# Quality Priority
reranker = FlashrankRerankAdapter(
    model_name="rank-T5-flan",
    top_n=5
)
```

## Best Practices

### Retrieve More, Rerank Less

Retrieve more documents initially, then rerank to fewer:

```python
# Retrieve 10-20 documents
base_retriever = vector_adapter.get_retriever(k=15)

# Rerank to top 5
reranker = FlashrankRerankAdapter(top_n=5)
compression_retriever = reranker.create_compression_retriever(base_retriever)
```

### Cache Directory

Use a persistent cache directory:

```python
config = LangChatConfig(
    reranker_cache_dir="rerank_models",  # Relative to working directory
    # or absolute path
    # reranker_cache_dir="/path/to/cache/rerank_models"
)
```

### Model Caching

Models are cached automatically:
- First download takes time
- Subsequent uses are instant
- Models persist across sessions

## Troubleshooting

### Issue: Model Download Fails

**Error:** `Failed to download model`

**Solution:**
- Check internet connection
- Verify model name is correct
- Check disk space
- Ensure write permissions on cache directory

### Issue: Import Errors

**Error:** `Could not import FlashrankRerank`

**Solution:**
```bash
pip install langchain langchain-community
pip install flashrank
```

### Issue: Slow Performance

**Solution:**
- Use smaller model (L-6 instead of L-12)
- Reduce retrieval count before reranking
- Use GPU if available (Flashrank supports GPU)

### Issue: Memory Issues

**Solution:**
- Use smaller models
- Reduce batch size
- Clear cache if needed

## Performance Optimization

### Model Selection

Choose based on your needs:
- **Speed**: `ms-marco-MiniLM-L-6-v2`
- **Balance**: `ms-marco-MiniLM-L-12-v2` (recommended)
- **Quality**: `rank-T5-flan`

### Batch Processing

Rerank multiple queries efficiently:

```python
# Process in batches
queries = ["query1", "query2", "query3"]
for query in queries:
    docs = compression_retriever.get_relevant_documents(query)
```

### Caching

Cache reranked results for repeated queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_rerank(query: str):
    return compression_retriever.get_relevant_documents(query)
```

## Integration Examples

### Example 1: Standard RAG Pipeline

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    # Vector database
    pinecone_api_key="pcsk-...",
    pinecone_index_name="kb",
    retrieval_k=10,  # Retrieve 10
    
    # Reranker
    reranker_top_n=5,  # Rerank to top 5
    
    # ... other config
)

langchat = LangChat(config=config)
# Automatically uses reranking in retrieval
```

### Example 2: Custom Reranking Setup

```python
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter

reranker = FlashrankRerankAdapter(
    model_name="ms-marco-MiniLM-L-12-v2",
    cache_dir="./models/rerank",
    top_n=3
)

# Use with custom retriever
compression_retriever = reranker.create_compression_retriever(
    base_retriever
)
```

### Example 3: Multiple Rerankers

```python
# Different rerankers for different use cases
fast_reranker = FlashrankRerankAdapter(
    model_name="ms-marco-MiniLM-L-6-v2",
    top_n=3
)

quality_reranker = FlashrankRerankAdapter(
    model_name="rank-T5-flan",
    top_n=5
)
```

## How Reranking Improves RAG

### Without Reranking

```
Query: "Python error handling"
↓
Vector Search returns:
1. "Python syntax basics" (score: 0.85)
2. "Error handling in Java" (score: 0.83)
3. "Python libraries" (score: 0.82)
```

### With Reranking

```
Query: "Python error handling"
↓
Vector Search returns 10 docs
↓
Reranking:
1. "Python error handling guide" (rerank score: 0.95)
2. "Exception handling in Python" (rerank score: 0.92)
3. "Python try-except blocks" (rerank score: 0.90)
```

## Related Documentation

- [Configuration Guide](../configuration.md)
- [Pinecone Adapter](pinecone_adapter.md)
- [LangChat Engine](../core/engine.md)
- [Flashrank Documentation](https://github.com/PrithivirajDamodaran/FlashRank)

