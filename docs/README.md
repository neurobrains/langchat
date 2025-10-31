# LangChat Documentation

## Overview   

LangChat is a powerful, modular conversational AI library with vector search capabilities. It's designed to be easily customizable and developer-friendly.

## Features

### 🤖 LLM Integration

- **OpenAI**: Native OpenAI API support with automatic API key rotation
- **Fault Tolerant**: Automatic retry logic with multiple API keys

### 🔍 Vector Search

- **Pinecone Integration**: Seamless vector database integration
- **Reranking**: Flashrank reranker for improved search results
- **Configurable Retrieval**: Adjustable document retrieval and reranking

### 💾 Database Management

- **Supabase**: Built-in Supabase integration
- **ID Management**: Automatic ID generation with conflict resolution
- **Session Management**: User-specific chat history and memory

### 🎨 Customization

- **Custom Prompts**: Configure both system prompts and standalone question prompts
- **Flexible Configuration**: Environment variables or direct configuration
- **Modular Architecture**: Use components independently or together

### 🚀 Developer Experience

- **Auto-Generated Interface**: Chat interface HTML auto-created on startup
- **Auto-Generated Dockerfile**: Dockerfile auto-created with correct port
- **Easy Setup**: Simple configuration and initialization

## Installation

```bash
pip install -e .
```

Or install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### As a Library

```python
from langchat import LangChat, LangChatConfig

# Create configuration
config = LangChatConfig(
    openai_api_keys=["your-api-key"],
    pinecone_api_key="your-pinecone-key",
    pinecone_index_name="your-index-name",
    supabase_url="your-supabase-url",
    supabase_key="your-supabase-key",
    server_port=8000
)

# Initialize
langchat = LangChat(config=config)

# Use it
result = await langchat.chat(
    query="Hello, how can you help me?",
    user_id="user123",
    domain="default"
)

print(result["response"])
```

### As an API Server

```python
# main.py
from langchat.api.app import create_app
from langchat.config import LangChatConfig

config = LangChatConfig(...)
app = create_app(config=config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.server_port, reload=True)
```

## Configuration

See [Configuration Guide](configuration.md) for detailed configuration options.

## Adapters Documentation

Comprehensive documentation for all LangChat adapters:

- [**Adapters Overview**](adapters/README.md) - Overview of all adapters
- [**OpenAI Service**](adapters/openai_service.md) - OpenAI API integration with key rotation
- [**Pinecone Adapter**](adapters/pinecone_adapter.md) - Vector database integration
- [**Flashrank Reranker**](adapters/flashrank_adapter.md) - Document reranking
- [**Supabase Adapter**](adapters/supabase_adapter.md) - Database operations
- [**ID Manager**](adapters/id_manager.md) - Sequential ID generation

## API Reference

See [API Reference](api_reference.md) for detailed API documentation. (Coming soon)

## Examples

See [Examples](../examples/) for various usage examples.