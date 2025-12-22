# LangChat Examples

This folder contains example implementations using LangChat.

## Available Examples

### Travel AI (`travel_ai.py`)

A complete example of building a travel assistance AI using LangChat.

**Features:**
- Custom system prompt for travel domain
- Custom standalone question prompt
- Multiple conversation examples
- Error handling

**Usage:**
```bash
python examples/travel_ai.py
```

**Configuration:**
1. Update API keys in the script
2. Configure your Pinecone index name
3. Configure your Supabase credentials
4. Run the example

### Education AI (`education_ai.py`)

A comprehensive example demonstrating LangChat with the **Adapter Pattern**.

**Features:**
- Custom educational prompts
- Demonstrates adapter pattern benefits
- Multi-user learning sessions
- Interactive educational chat
- Shows how to swap providers easily

**Usage:**
```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export PINECONE_API_KEY="your-key"
export PINECONE_INDEX_NAME="your-index"
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"

# Run the example
python examples/education_ai.py
```

**What it demonstrates:**
1. **Basic Usage**: Using default providers (OpenAI, Pinecone, Supabase, FlashRank)
2. **Adapter Pattern**: How the abstraction layer works and its benefits
3. **Multi-User Sessions**: Separate learning contexts for different students
4. **Interactive Chat**: Real-time educational conversations

**Key Concepts:**
- The adapter pattern decouples core logic from specific providers
- Easy to swap providers (e.g., OpenAI → Anthropic, Pinecone → Chroma)
- Type-safe with abstract base classes
- Backward compatible - defaults remain the same

**Configuration:**
1. Set environment variables (see above)
2. Or update the config directly in the script
3. Run the example

## Creating Your Own Example

1. Copy `travel_ai.py` or `education_ai.py` as a template
2. Customize the system prompt for your domain
3. Update configuration with your credentials
4. Add domain-specific examples
5. Run and test!

## More Examples Coming Soon

- Customer Support AI
- Healthcare Chatbot
- E-commerce Assistant
