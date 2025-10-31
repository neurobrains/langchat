# Adapters Documentation

This directory contains comprehensive documentation for all LangChat adapters. Adapters are modular components that handle integration with external services.

## Overview

LangChat uses a modular adapter architecture where each adapter is responsible for a specific external service:

- **Services**: LLM providers (OpenAI)
- **Vector DB**: Vector database providers (Pinecone)
- **Reranker**: Reranking services (Flashrank)
- **Database**: Database adapters (Supabase)

## Available Adapters

### LLM Service Adapters
- [OpenAI Service](openai_service.md) - OpenAI API integration with automatic key rotation

### Vector Database Adapters
- [Pinecone Adapter](pinecone_adapter.md) - Pinecone vector database integration

### Reranker Adapters
- [Flashrank Reranker](flashrank_adapter.md) - Document reranking with Flashrank

### Database Adapters
- [Supabase Adapter](supabase_adapter.md) - Supabase database operations
- [ID Manager](id_manager.md) - Sequential ID generation with conflict resolution

## Architecture

Each adapter follows a consistent pattern:

1. **Initialization**: Configure connection with external service
2. **Error Handling**: Robust error handling and retry logic
3. **Integration**: Seamless integration with LangChat core components

## Usage Pattern

All adapters are initialized through the `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    # Adapter configurations
    openai_api_keys=["key1", "key2"],
    pinecone_api_key="pcsk-...",
    pinecone_index_name="my-index",
    supabase_url="https://...",
    supabase_key="eyJ..."
)

langchat = LangChat(config=config)
# All adapters are automatically initialized
```

## Extending Adapters

To add a new adapter:

1. Create a new adapter class following existing patterns
2. Implement required methods
3. Add configuration options to `LangChatConfig`
4. Integrate with `LangChatEngine`

See individual adapter documentation for specific implementation details.

