# OpenAI Service Adapter

The OpenAI Service Adapter provides integration with OpenAI's API, featuring automatic API key rotation and fault-tolerant retry logic.

## Overview

The `OpenAILLMService` is a production-ready wrapper around OpenAI's Chat API that provides:

- **Automatic API Key Rotation**: Seamlessly rotate between multiple API keys
- **Fault Tolerance**: Automatic retry with key rotation on failures
- **Error Recovery**: Handles rate limits and API errors gracefully

## Features

### 🔄 Automatic API Key Rotation

When configured with multiple API keys, the service automatically rotates between them:
- On API failures
- On rate limit errors
- When a key is exhausted

### 🛡️ Fault Tolerance

Built-in retry mechanism:
- Automatic retry on failures
- Key rotation on errors
- Configurable retry attempts per key

### ⚡ Performance

- Efficient key cycling using Python's `itertools.cycle`
- Lazy initialization of ChatOpenAI instances
- Minimal overhead

## Configuration

The service is configured through `LangChatConfig`:

```python
from langchat.config import LangChatConfig

config = LangChatConfig(
    openai_api_keys=["sk-...", "sk-...", "sk-..."],  # Multiple keys for rotation
    openai_model="gpt-4o-mini",
    openai_temperature=1.0,
    max_llm_retries=2  # Retries per key
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `openai_api_keys` | `List[str]` | Required | List of OpenAI API keys for rotation |
| `openai_model` | `str` | `"gpt-4o-mini"` | OpenAI model to use |
| `openai_temperature` | `float` | `1.0` | Model temperature (0.0-2.0) |
| `max_llm_retries` | `int` | `2` | Number of retries per API key |

## Usage

### Basic Usage

The service is automatically initialized by `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    openai_api_keys=["your-api-key"],
    # ... other config
)

langchat = LangChat(config=config)
# Service is automatically initialized
```

### Direct Usage (Advanced)

```python
from langchat.adapters.services.openai_service import OpenAILLMService

service = OpenAILLMService(
    model="gpt-4o-mini",
    temperature=1.0,
    api_keys=["sk-...", "sk-..."],
    max_retries_per_key=2
)

# Use the service
messages = [{"role": "user", "content": "Hello!"}]
response = service.invoke(messages)
```

## API Reference

### Class: `OpenAILLMService`

#### Constructor

```python
OpenAILLMService(
    model: str,
    temperature: float,
    api_keys: List[str],
    max_retries_per_key: int = 2
)
```

**Parameters:**
- `model` (str): OpenAI model name (e.g., "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo")
- `temperature` (float): Model temperature (0.0-2.0)
- `api_keys` (List[str]): List of OpenAI API keys for rotation
- `max_retries_per_key` (int): Maximum retries per API key (default: 2)

#### Methods

##### `invoke(messages, **kwargs)`

Invoke the OpenAI Chat API with automatic retry and key rotation.

**Parameters:**
- `messages`: List of message dictionaries (LangChain format)
- `**kwargs`: Additional arguments passed to ChatOpenAI

**Returns:**
- AI model response

**Raises:**
- `Exception`: If all API keys are exhausted

**Example:**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"}
]

response = service.invoke(messages)
print(response.content)
```

## How It Works

### Key Rotation Flow

```
1. Initialize with list of API keys
2. Use first key for API calls
3. On failure:
   a. Rotate to next key
   b. Retry the request
   c. If all keys exhausted, raise exception
4. On success, continue with current key
```

### Retry Logic

The service implements intelligent retry:
- **Per Key Retries**: Each key gets `max_retries_per_key` attempts
- **Total Retries**: Total attempts = `len(api_keys) × max_retries_per_key`
- **Error Handling**: Distinguishes between retryable and non-retryable errors

## Best Practices

### Multiple API Keys

Use multiple API keys to:
- Handle rate limits
- Distribute load
- Improve fault tolerance

```python
config = LangChatConfig(
    openai_api_keys=[
        "sk-org1-key1",
        "sk-org1-key2",
        "sk-org2-key1"  # Different organization
    ],
    max_llm_retries=2
)
```

### Error Handling

The service handles common errors:
- **Rate Limits**: Automatically rotates keys
- **API Errors**: Retries with different key
- **Network Errors**: Retries with exponential backoff (via LangChain)

### Monitoring

Monitor API usage:
- Track which keys are being used
- Monitor error rates
- Watch for exhausted keys

```python
# Check current key (for monitoring)
current_key_prefix = service.current_key[:8] + "..."
print(f"Using key: {current_key_prefix}")
```

## Troubleshooting

### Issue: All API Keys Exhausted

**Solution:** 
- Add more API keys
- Increase `max_llm_retries`
- Check API key validity

### Issue: Rate Limit Errors

**Solution:**
- Use more API keys from different organizations
- Reduce request frequency
- Implement request queuing

### Issue: Invalid API Keys

**Solution:**
- Verify key format starts with "sk-"
- Check key hasn't expired
- Ensure key has proper permissions

## Integration with LangChain

The adapter uses LangChain's `ChatOpenAI` under the hood:

```python
from langchain_openai import ChatOpenAI

# Each key creates a separate ChatOpenAI instance
llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    openai_api_key=api_key,
    max_retries=1
)
```

This provides:
- LangChain compatibility
- Standard message format
- Built-in retry mechanisms

## Performance Considerations

- **Key Switching Overhead**: Minimal (just key rotation)
- **LLM Initialization**: Lazy (only when needed)
- **Memory Usage**: One ChatOpenAI instance per active key

## Examples

### Example 1: Single Key

```python
service = OpenAILLMService(
    model="gpt-4o-mini",
    temperature=0.7,
    api_keys=["sk-single-key"],
    max_retries_per_key=3
)
```

### Example 2: Multiple Keys for High Availability

```python
service = OpenAILLMService(
    model="gpt-4",
    temperature=1.0,
    api_keys=[
        "sk-key-1",
        "sk-key-2",
        "sk-key-3",
        "sk-key-4"
    ],
    max_retries_per_key=2  # Total: 8 retries
)
```

### Example 3: Production Configuration

```python
config = LangChatConfig(
    openai_api_keys=os.getenv("OPENAI_API_KEYS").split(","),
    openai_model="gpt-4o-mini",
    openai_temperature=0.8,
    max_llm_retries=2
)
```

## Related Documentation

- [Configuration Guide](../configuration.md)
- [LangChat Engine](../core/engine.md)
- [Core Components](../core/README.md)

