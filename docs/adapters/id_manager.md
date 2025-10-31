# ID Manager

The ID Manager provides automatic sequential ID generation with conflict resolution for Supabase tables.

## Overview

The `IDManager` handles ID generation for database tables, ensuring:

- **Sequential IDs**: Generate sequential integer IDs
- **Conflict Resolution**: Automatic retry on ID conflicts
- **Database Sync**: Synchronizes with database state
- **Error Recovery**: Robust error handling and recovery

## Features

### 🔢 Sequential ID Generation

Generate sequential IDs automatically:
- No manual ID management needed
- Thread-safe ID generation
- Efficient counter management

### 🔄 Conflict Resolution

Automatic conflict handling:
- Detects ID conflicts
- Retries with new ID
- Syncs with database state

### 🗄️ Database Synchronization

Keeps counters in sync with database:
- Initializes from database
- Updates on conflicts
- Handles concurrent inserts

## Configuration

The ID Manager is initialized automatically:

```python
from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter

# Initialize adapter
adapter = SupabaseAdapter(url="...", key="...")

# Initialize ID manager
id_manager = IDManager(
    supabase_client=adapter.client,
    initial_value=1,  # Starting ID
    retry_attempts=3  # Retry attempts on conflict
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `supabase_client` | `Client` | Required | Supabase client instance |
| `initial_value` | `int` | `1` | Starting ID value |
| `retry_attempts` | `int` | `3` | Number of retry attempts on conflict |

## Usage

### Basic Usage

The ID Manager is automatically initialized by `LangChatEngine`:

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    supabase_url="https://xxxxx.supabase.co",
    supabase_key="eyJhbGc...",
    # ... other config
)

langchat = LangChat(config=config)
# ID Manager is automatically initialized
```

### Direct Usage (Advanced)

```python
from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter

# Initialize
adapter = SupabaseAdapter(url="...", key="...")
id_manager = IDManager(
    supabase_client=adapter.client,
    initial_value=1
)

# Initialize counters from database
id_manager.initialize()

# Get next ID
next_id = id_manager.next_id("chat_history")
print(f"Next ID: {next_id}")

# Insert with automatic ID
result = id_manager.insert_with_retry(
    table_name="chat_history",
    data={
        "user_id": "user123",
        "query": "Hello",
        "response": "Hi there!"
    }
)
```

## API Reference

### Class: `IDManager`

#### Constructor

```python
IDManager(
    supabase_client: Client,
    initial_value: int = 1,
    retry_attempts: int = 3
)
```

**Parameters:**
- `supabase_client` (Client): Supabase client instance
- `initial_value` (int): Starting ID value (default: 1)
- `retry_attempts` (int): Number of retry attempts on conflict (default: 3)

#### Methods

##### `initialize()`

Initialize ID counters from the database.

Fetches row count and maximum ID from each table and sets counters accordingly.

**Example:**
```python
id_manager.initialize()
# Counters synced with database
```

##### `next_id(table_name: str) -> int`

Get the next available ID for the specified table.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:**
- `int`: Next available ID

**Example:**
```python
next_id = id_manager.next_id("chat_history")
# Returns: 42
```

##### `insert_with_retry(table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]`

Insert data into the specified table with automatic ID generation and retry on conflicts.

**Parameters:**
- `table_name` (str): Name of the table to insert into
- `data` (Dict[str, Any]): Dictionary of data to insert (without ID)

**Returns:**
- `Optional[Dict[str, Any]]`: Response data if successful, None if all retries failed

**Example:**
```python
result = id_manager.insert_with_retry(
    table_name="chat_history",
    data={
        "user_id": "user123",
        "query": "What is Python?",
        "response": "Python is a programming language..."
    }
)

if result:
    print(f"Inserted with ID: {result[0]['id']}")
else:
    print("Insert failed after retries")
```

## How It Works

### Initialization Process

```
1. Query database for each table
   ↓
2. Get row count
   ↓
3. Get maximum ID
   ↓
4. Set counter to max(row_count + 1, max_id + 1, initial_value)
   ↓
5. Counters ready for use
```

### ID Generation Flow

```
1. Get current counter for table
   ↓
2. Increment counter
   ↓
3. Return ID
   ↓
4. Counter ready for next ID
```

### Conflict Resolution Flow

```
1. Generate ID
   ↓
2. Attempt insert
   ↓
3. If conflict:
   a. Log warning
   b. Re-sync counter from database
   c. Wait briefly (0.2s)
   d. Retry with new ID
   ↓
4. If all retries fail:
   a. Log error
   b. Return None
```

## Supported Tables

The ID Manager automatically handles these tables:

- `chat_history` - User conversation history
- `request_metrics` - Request performance metrics
- `feedback` - User feedback

### Adding Custom Tables

To add support for custom tables:

```python
# Initialize custom table counter
id_manager._initialize_table("custom_table")

# Use with custom table
id_manager.next_id("custom_table")
id_manager.insert_with_retry("custom_table", {...})
```

## Best Practices

### Initialization

Always initialize before use:

```python
id_manager = IDManager(supabase_client=client)
id_manager.initialize()  # Sync with database
```

### Error Handling

Handle insert failures:

```python
result = id_manager.insert_with_retry(
    table_name="chat_history",
    data={...}
)

if not result:
    # Handle failure
    logger.error("Failed to insert after retries")
    # Fallback logic
```

### Retry Configuration

Adjust retry attempts based on load:

```python
# High concurrency: More retries
id_manager = IDManager(
    supabase_client=client,
    retry_attempts=5  # More retries
)

# Low concurrency: Fewer retries
id_manager = IDManager(
    supabase_client=client,
    retry_attempts=2  # Fewer retries
)
```

## Conflict Scenarios

### Scenario 1: Concurrent Inserts

```
Thread 1: Gets ID 42, starts insert
Thread 2: Gets ID 42, starts insert
Thread 1: Inserts ID 42 ✓
Thread 2: Conflict detected → Retry with ID 43 ✓
```

### Scenario 2: Database Gap

```
Database has IDs: 1, 2, 5, 7 (missing 3, 4, 6)
Counter initialized: max(max_id=7, row_count=4) + 1 = 8
Next ID: 8 ✓ (fills gaps naturally)
```

### Scenario 3: Manual Inserts

```
Manual insert with ID 100
Counter syncs: max(100, counter) = 100
Next ID: 101 ✓
```

## Troubleshooting

### Issue: ID Conflicts Persist

**Problem:** Frequent ID conflicts

**Solution:**
- Increase `retry_attempts`
- Reduce concurrent inserts
- Check for manual inserts
- Verify database constraints

### Issue: Counter Out of Sync

**Problem:** Generated IDs don't match database

**Solution:**
- Re-initialize: `id_manager.initialize()`
- Check for manual inserts
- Verify database state

### Issue: Insert Failures

**Problem:** `insert_with_retry` returns None

**Solution:**
- Check database connection
- Verify table exists
- Check data format
- Review error logs

## Performance Considerations

### Counter Management

Counters are in-memory:
- Fast ID generation
- Minimal database queries
- Efficient for high-throughput

### Database Sync

Sync happens:
- On initialization
- On conflict detection
- Can be forced: `initialize()`

### Concurrent Access

The manager handles concurrent access:
- Thread-safe counter increment
- Automatic conflict resolution
- Suitable for multi-threaded environments

## Integration Examples

### Example 1: Basic Usage

```python
from langchat.adapters.supabase.id_manager import IDManager

id_manager = IDManager(supabase_client=client)
id_manager.initialize()

next_id = id_manager.next_id("chat_history")
print(f"Next ID: {next_id}")
```

### Example 2: Automatic Insert

```python
result = id_manager.insert_with_retry(
    table_name="chat_history",
    data={
        "user_id": "user123",
        "domain": "education",
        "query": "Hello",
        "response": "Hi!"
    }
)
```

### Example 3: Custom Table

```python
# Initialize custom table
id_manager._initialize_table("custom_logs")

# Use custom table
id_manager.insert_with_retry(
    table_name="custom_logs",
    data={"message": "Log entry"}
)
```

### Example 4: Error Handling

```python
result = id_manager.insert_with_retry(
    table_name="chat_history",
    data={...}
)

if result is None:
    # Fallback: Manual insert with UUID
    import uuid
    manual_id = uuid.uuid4()
    client.table("chat_history").insert({
        "id": str(manual_id),
        **data
    }).execute()
```

## Related Documentation

- [Supabase Adapter](supabase_adapter.md)
- [Configuration Guide](../configuration.md)
- [LangChat Engine](../core/engine.md)

