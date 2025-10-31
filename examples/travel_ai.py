"""
Main entry point for running LangChat API server.
This uses the langchat library from src/langchat.
"""

import logging
from langchat.config import LangChatConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TRAVEL_SYSTEM_PROMPT = """You are a helpful travel assistant specializing in trip planning, recommendations, and travel information.

Your expertise includes:
- Destination recommendations based on budget and preferences
- Flight and hotel booking guidance
- Local attractions and activities
- Travel tips and safety information
- Cultural insights and local customs
- Visa and travel document requirements

Be friendly, concise, and helpful. Provide practical, actionable advice.

Use the following context to answer questions:
{context}

Chat history: {chat_history}

Question: {question}
Answer:"""

# Custom standalone question prompt for travel
TRAVEL_STANDALONE_PROMPT = """Convert this travel-related question to a standalone search query.
Make sure the query captures the intent for finding relevant travel information.

Chat History: {chat_history}
Question: {question}
Standalone query:"""

def main():
    """Main function to start the LangChat API server"""
    from langchat.api.app import create_app
    import uvicorn
        
    # Create configuration
    # You can customize this or use environment variables
    config = LangChatConfig(
        openai_api_keys=[
            "your-openai-api-key"
        ],
        pinecone_api_key="your-pinecone-api-key",
        pinecone_index_name="your-pinecone-index-name",
        supabase_url="your-supabase-url",
        supabase_key="your-supabase-api-key",
        # Custom Prompts
        system_prompt_template=TRAVEL_SYSTEM_PROMPT,
        standalone_question_prompt=TRAVEL_STANDALONE_PROMPT,
        server_port=8007  # Configure your port
    )
    
    # Create FastAPI app
    app = create_app(config=config, auto_generate_interface=True, auto_generate_docker=True)
    
    # Start the server
    logger.info(f"🚀 Starting LangChat API server on port {config.server_port}")
    uvicorn.run(app, host="0.0.0.0", port=config.server_port, reload=False)

# Running the Server
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Make sure you've configured your API keys correctly.")