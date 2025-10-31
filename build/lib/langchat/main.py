"""
LangChat - Main entry point for developers.
This module provides an easy-to-use interface for creating conversational AI applications.
"""

import asyncio
import logging
from typing import Optional
from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangChat:
    """
    Main LangChat class for developers.
    Easy to use and highly customizable.
    """
    
    def __init__(self, config: Optional[LangChatConfig] = None):
        """
        Initialize LangChat instance.
        
        Args:
            config: LangChat configuration. If None, creates config from environment variables.
        
        Example:
            ```python
            from langchat import LangChat, LangChatConfig
            
            # Create custom config
            config = LangChatConfig(
                openai_api_keys=["your-api-key"],
                pinecone_api_key="your-pinecone-key",
                supabase_url="your-supabase-url",
                supabase_key="your-supabase-key"
            )
            
            # Initialize LangChat
            langchat = LangChat(config=config)
            ```
        """
        self.config = config or LangChatConfig.from_env()
        self.engine = LangChatEngine(config=self.config)
        logger.info("LangChat initialized successfully")
    
    async def chat(
        self,
        query: str,
        user_id: str,
        domain: str = "default"
    ) -> dict:
        """
        Process a chat query.
        
        Args:
            query: User query text
            user_id: User ID
            domain: User domain (optional, defaults to "default")
        
        Returns:
            Dictionary with response and metadata
        
        Example:
            ```python
            result = await langchat.chat(
                query="What are the best universities in Europe?",
                user_id="user123",
                domain="education"
            )
            print(result["response"])
            ```
        """
        return await self.engine.chat(
            query=query,
            user_id=user_id,
            domain=domain
        )
    
    def chat_sync(
        self,
        query: str,
        user_id: str,
        domain: str = "default"
    ) -> dict:
        """
        Synchronous version of chat method.
        
        Args:
            query: User query text
            user_id: User ID
            domain: User domain (optional, defaults to "default")
        
        Returns:
            Dictionary with response and metadata
        
        Example:
            ```python
            result = langchat.chat_sync(
                query="What are the best universities in Europe?",
                user_id="user123"
            )
            print(result["response"])
            ```
        """
        return asyncio.run(self.chat(query, user_id, domain))
    
    def get_session(self, user_id: str, domain: str = "default"):
        """
        Get or create a user session.
        
        Args:
            user_id: User ID
            domain: User domain
        
        Returns:
            UserSession instance
        
        Example:
            ```python
            session = langchat.get_session(user_id="user123", domain="education")
            # Access session properties
            print(session.chat_history)
            ```
        """
        return self.engine.get_session(user_id, domain)


# Example usage
if __name__ == "__main__":
    # Initialize LangChat with custom config
    config = LangChatConfig(
        openai_api_keys=["your-openai-api-key"],
        openai_model="gpt-4o-mini",
        pinecone_api_key="your-pinecone-api-key",
        pinecone_index_name="your-index-name",
        supabase_url="your-supabase-url",
        supabase_key="your-supabase-key"
    )
    
    # Create LangChat instance
    langchat = LangChat(config=config)
    
    # Example: Process a chat query
    async def example():
        result = await langchat.chat(
            query="Hello, how are you?",
            user_id="user123",
            domain="default"
        )
        print(f"Response: {result['response']}")
    
    # Run example
    # asyncio.run(example())
