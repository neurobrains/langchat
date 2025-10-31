# Configuration Guide

## LangChatConfig

All configuration is done through the `LangChatConfig` class.

### Basic Configuration

```python
from langchat import LangChatConfig

config = LangChatConfig(
    openai_api_keys=["your-api-key"],
    pinecone_api_key="your-pinecone-key",
    pinecone_index_name="your-index-name",
    supabase_url="your-supabase-url",
    supabase_key="your-supabase-key"
)
```


### Custom Prompts

```python
config = LangChatConfig(
    # ... other config ...
    system_prompt_template="""You are a helpful assistant.
    Use the following context to answer questions:
    {context}
    
    Chat history: {chat_history}
    
    Question: {question}
    Answer:""",
    standalone_question_prompt="""Convert this question to a standalone query:
    Chat History: {chat_history}
    Question: {question}
    Standalone query:"""
)
```

### Environment Variables

```bash
export OPENAI_API_KEYS="key1,key2"
export PINECONE_API_KEY="your-key"
export PINECONE_INDEX_NAME="your-index"
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"
export PORT=8000
```

Then use:
```python
config = LangChatConfig.from_env()
```

## Configuration Options

### OpenAI Configuration
- `openai_api_keys`: List of OpenAI API keys (for rotation)
- `openai_model`: Model name (default: "gpt-4o-mini")
- `openai_temperature`: Temperature (default: 1.0)
- `openai_embedding_model`: Embedding model (default: "text-embedding-3-large")

### Pinecone Configuration
- `pinecone_api_key`: Pinecone API key (required)
- `pinecone_index_name`: Index name (required)

### Supabase Configuration
- `supabase_url`: Supabase project URL (required)
- `supabase_key`: Supabase API key (required)

### Vector Search Configuration
- `retrieval_k`: Number of documents to retrieve (default: 5)
- `reranker_top_n`: Top N after reranking (default: 3)
- `reranker_model`: Reranker model name
- `reranker_cache_dir`: Auto-configured to src/langchat/models/rerank_models

### Session Configuration
- `max_chat_history`: Maximum messages in history (default: 20)
- `memory_window`: Conversation buffer window (default: 20)

### Server Configuration
- `server_port`: Port number for API server (default: 8000)
