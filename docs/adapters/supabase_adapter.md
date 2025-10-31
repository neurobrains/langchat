# Supabase Adapter

The Supabase Adapter provides integration with Supabase PostgreSQL database for storing chat history, metrics, and feedback.

## Overview

The `SupabaseAdapter` is a lightweight wrapper around Supabase's Python client that provides:

- **Database Operations**: CRUD operations on Supabase tables
- **Connection Management**: Efficient client initialization
- **Error Handling**: Robust error handling
- **Integration**: Seamless integration with LangChat components

## Features

### 💾 Database Operations

Easy access to Supabase tables:
- Insert records
- Query data
- Update records
- Delete records

### 🔗 Connection Management

Efficient client management:
- Lazy initialization
- Singleton pattern
- Connection reuse

### 🛡️ Error Handling

Robust error handling:
- Connection errors
- Query errors
- Timeout handling

## Configuration

Configure through `LangChatConfig`:

```python
from langchat.config import LangChatConfig

config = LangChatConfig(
    supabase_url="https://xxxxx.supabase.co",
    supabase_key="eyJhbGc..."  # anon or service role key
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `supabase_url` | `str` | Required | Supabase project URL |
| `supabase_key` | `str` | Required | Supabase API key (anon or service role) |

## Usage

### Basic Usage

The adapter is automatically initialized by `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    supabase_url="https://xxxxx.supabase.co",
    supabase_key="eyJhbGc...",
    # ... other config
)

langchat = LangChat(config=config)
# Adapter is automatically initialized
```

### Direct Usage (Advanced)

```python
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter

adapter = SupabaseAdapter(
    url="https://xxxxx.supabase.co",
    key="eyJhbGc..."
)

# Access Supabase client
client = adapter.client

# Perform operations
result = client.table("chat_history").select("*").execute()
```

## API Reference

### Class: `SupabaseAdapter`

#### Constructor

```python
SupabaseAdapter(
    url: str,
    key: str
)
```

**Parameters:**
- `url` (str): Supabase project URL
- `key` (str): Supabase API key (anon or service role)

#### Class Method

##### `from_config(supabase_url: str, supabase_key: str)`

Create adapter from configuration parameters.

**Parameters:**
- `supabase_url` (str): Supabase project URL
- `supabase_key` (str): Supabase API key

**Returns:**
- `SupabaseAdapter`: New adapter instance

#### Properties

##### `client`

Get or create Supabase client instance.

**Returns:**
- `Client`: Supabase client instance

**Example:**
```python
client = adapter.client
result = client.table("chat_history").select("*").execute()
```

## Database Schema

LangChat uses the following tables in Supabase:

### chat_history

Stores user conversation history.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-generated) |
| `user_id` | String | User identifier |
| `domain` | String | Conversation domain |
| `query` | Text | User query |
| `response` | Text | AI response |
| `timestamp` | Timestamp | Message timestamp |
| `session_id` | String | Session identifier |

### request_metrics

Stores request performance metrics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-generated) |
| `user_id` | String | User identifier |
| `domain` | String | Request domain |
| `response_time` | Float | Response time in seconds |
| `timestamp` | Timestamp | Request timestamp |
| `status` | String | Request status |

### feedback

Stores user feedback on responses.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-generated) |
| `user_id` | String | User identifier |
| `domain` | String | Feedback domain |
| `response` | Text | Original response |
| `feedback_text` | Text | User feedback text |
| `rating` | Integer | Rating (1 = like, 0 = dislike) |
| `timestamp` | Timestamp | Feedback timestamp |

## Supabase Setup

### 1. Create Supabase Project

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Wait for database to initialize

### 2. Get API Credentials

1. Go to Project Settings → API
2. Copy Project URL
3. Copy anon/public key or service_role key

**Key Types:**
- **anon key**: For client-side operations (has Row Level Security)
- **service_role key**: For server-side operations (bypasses RLS)

### 3. Create Tables

Run this SQL in Supabase SQL Editor:

```sql
-- Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    session_id TEXT
);

-- Create request_metrics table
CREATE TABLE IF NOT EXISTS request_metrics (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    response_time FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    status TEXT
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    response TEXT,
    feedback_text TEXT,
    rating INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_domain ON chat_history(domain);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);
```

### 4. Configure Row Level Security (Optional)

For production, configure RLS policies:

```sql
-- Enable RLS
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust as needed)
CREATE POLICY "Allow service role full access" ON chat_history
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access" ON request_metrics
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access" ON feedback
    FOR ALL USING (auth.role() = 'service_role');
```

## Best Practices

### Key Selection

Choose appropriate key:
- **Development**: Use `anon` key with RLS disabled
- **Production**: Use `service_role` key (keep secure!)

### Connection Management

The adapter uses lazy initialization:
- Client created on first access
- Reused for subsequent operations
- Efficient connection pooling

### Error Handling

Handle Supabase errors:

```python
try:
    result = adapter.client.table("chat_history").select("*").execute()
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    # Handle error
```

### Query Optimization

Use indexes:
- Index on `user_id` for user queries
- Index on `domain` for domain filtering
- Index on `timestamp` for time-based queries

## Common Operations

### Insert Record

```python
client = adapter.client

result = client.table("chat_history").insert({
    "user_id": "user123",
    "domain": "education",
    "query": "What is Python?",
    "response": "Python is a programming language...",
    "session_id": "session-123"
}).execute()
```

### Query Records

```python
# Get user's chat history
result = client.table("chat_history") \
    .select("*") \
    .eq("user_id", "user123") \
    .order("timestamp", desc=True) \
    .limit(10) \
    .execute()

# Get records by domain
result = client.table("chat_history") \
    .select("*") \
    .eq("domain", "education") \
    .execute()
```

### Update Record

```python
result = client.table("chat_history") \
    .update({"response": "Updated response"}) \
    .eq("id", 123) \
    .execute()
```

### Delete Record

```python
result = client.table("chat_history") \
    .delete() \
    .eq("id", 123) \
    .execute()
```

## Troubleshooting

### Issue: Connection Failed

**Error:** `Failed to connect to Supabase`

**Solution:**
- Verify URL is correct (includes https://)
- Check internet connection
- Verify project is active

### Issue: Invalid API Key

**Error:** `Invalid API key`

**Solution:**
- Verify key format (starts with `eyJ`)
- Check if using correct key type
- Ensure key hasn't been rotated

### Issue: Table Not Found

**Error:** `Table 'xxx' not found`

**Solution:**
- Verify table exists in Supabase dashboard
- Check table name spelling
- Ensure proper permissions

### Issue: Permission Denied

**Error:** `Permission denied`

**Solution:**
- Check RLS policies
- Use service_role key for server-side operations
- Verify API key permissions

## Performance Optimization

### Indexing

Create indexes for frequently queried columns:

```sql
CREATE INDEX idx_user_domain ON chat_history(user_id, domain);
CREATE INDEX idx_timestamp_desc ON chat_history(timestamp DESC);
```

### Query Optimization

Use efficient queries:

```python
# Good: Use filters
result = client.table("chat_history") \
    .select("*") \
    .eq("user_id", user_id) \
    .limit(20) \
    .execute()

# Bad: Select all then filter
result = client.table("chat_history").select("*").execute()
# Then filter in Python (inefficient)
```

### Connection Pooling

Supabase client handles connection pooling automatically:
- Reuses connections
- Efficient resource usage
- No manual pooling needed

## Integration with ID Manager

The adapter works seamlessly with `IDManager`:

```python
from langchat.adapters.supabase.id_manager import IDManager

id_manager = IDManager(
    supabase_client=adapter.client,
    initial_value=1
)

# ID manager uses adapter.client for ID generation
next_id = id_manager.next_id("chat_history")
```

## Related Documentation

- [Configuration Guide](../configuration.md)
- [ID Manager](id_manager.md)
- [LangChat Engine](../core/engine.md)
- [Supabase Documentation](https://supabase.com/docs)

