"""
LangChat Engine - Main entry point for using LangChat.
"""

import logging
import os
import time
from typing import Dict, Optional
from datetime import datetime, timezone

from langchat.config import LangChatConfig
from langchat.core.session import UserSession
from langchat.core.prompts import generate_standalone_question
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter
from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.services.openai_service import OpenAILLMService
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter

logger = logging.getLogger(__name__)


class LangChatEngine:
    """
    Main engine for LangChat library.
    Developers use this to create conversational AI applications.
    """
    
    def __init__(self, config: Optional[LangChatConfig] = None):
        """
        Initialize LangChat engine.
        
        Args:
            config: LangChat configuration. If None, uses default config.
        """
        self.config = config or LangChatConfig.from_env()
        
        # Initialize adapters
        self._initialize_adapters()
        
        # Initialize database
        self._initialize_database()
        
        # Sessions storage
        self.sessions: Dict[str, UserSession] = {}
        
        logger.info("LangChat Engine initialized successfully")
    
    def _initialize_adapters(self):
        """Initialize all adapters."""
        # Initialize Supabase adapter
        if self.config.supabase_url and self.config.supabase_key:
            self.supabase_adapter = SupabaseAdapter.from_config(
                self.config.supabase_url,
                self.config.supabase_key
            )
        else:
            raise ValueError("Supabase URL and key must be provided")
        
        # Initialize ID manager
        self.id_manager = IDManager(
            self.supabase_adapter.client,
            initial_value=0,
            retry_attempts=5
        )
        
        # Initialize LLM service (OpenAI)
        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be provided")
        self.llm = OpenAILLMService(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            api_keys=self.config.openai_api_keys,
            max_retries_per_key=self.config.max_llm_retries
        )
        
        # Initialize Pinecone vector adapter
        if not self.config.pinecone_api_key:
            raise ValueError("Pinecone API key must be provided")
        if not self.config.pinecone_index_name:
            raise ValueError("Pinecone index name must be provided")
        
        # Get embedding API key (OpenAI)
        embedding_api_key = self.config.openai_api_keys[0] if self.config.openai_api_keys else None
        
        self.vector_adapter = PineconeVectorAdapter(
            api_key=self.config.pinecone_api_key,
            index_name=self.config.pinecone_index_name,
            embedding_model=self.config.openai_embedding_model,
            embedding_api_key=embedding_api_key
        )
        
        # Initialize Flashrank reranker
        # Use config's reranker_cache_dir (relative to current working directory)
        reranker_cache_dir = self.config.reranker_cache_dir
        os.makedirs(reranker_cache_dir, exist_ok=True)
        logger.info(f"Reranker cache directory created/verified: {reranker_cache_dir}")
        
        # Initialize ranker (this will download the model if not already present)
        self.reranker_adapter = FlashrankRerankAdapter(
            model_name=self.config.reranker_model,
            cache_dir=reranker_cache_dir,
            top_n=self.config.reranker_top_n
        )
        logger.info(f"Reranker model '{self.config.reranker_model}' initialized")
    
    def _initialize_database(self):
        """Initialize database tables."""
        try:
            # Check if tables exist
            self.supabase_adapter.client.table("chat_history").select("id").limit(1).execute()
            self.supabase_adapter.client.table("request_metrics").select("id").limit(1).execute()
            self.supabase_adapter.client.table("feedback").select("id").limit(1).execute()
            logger.info("Database tables already exist")
        except Exception:
            # Initialize ID manager to set up counters
            self.id_manager.initialize()
            
            # Create initial records to ensure tables exist
            try:
                self.id_manager.insert_with_retry("chat_history", {
                    "user_id": "system",
                    "domain": "system",
                    "query": "init",
                    "response": "init",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                self.id_manager.insert_with_retry("request_metrics", {
                    "user_id": "system",
                    "request_time": datetime.now(timezone.utc).isoformat(),
                    "response_time": 0.0,
                    "success": True,
                    "error_message": None
                })
                
                self.id_manager.insert_with_retry("feedback", {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "system",
                    "user_id": "system",
                    "domain": "system",
                    "response": "init",
                    "feedback_text": "init",
                    "rating": 1
                })
                
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Error creating database tables: {str(e)}")
    
    def get_session(self, user_id: str, domain: str = "default") -> UserSession:
        """
        Get or create a user session.
        
        Args:
            user_id: User ID
            domain: User domain
        
        Returns:
            UserSession instance
        """
        session_key = f"{user_id}_{domain}"
        
        if session_key not in self.sessions:
            # Get prompt template
            prompt_template = self.config.system_prompt_template or self.config.get_default_prompt_template()
            
            self.sessions[session_key] = UserSession(
                domain=domain,
                user_id=user_id,
                config=self.config,
                llm=self.llm,
                vector_adapter=self.vector_adapter,
                reranker_adapter=self.reranker_adapter,
                supabase_adapter=self.supabase_adapter,
                id_manager=self.id_manager,
                prompt_template=prompt_template
            )
        
        return self.sessions[session_key]
    
    async def chat(
        self,
        query: str,
        user_id: str,
        domain: str = "default",
        standalone_question: Optional[str] = None
    ) -> dict:
        """
        Process a chat query.
        
        Args:
            query: User query
            user_id: User ID
            domain: User domain
            standalone_question: Optional standalone question (if already generated)
        
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            # Get or create session
            session = self.get_session(user_id, domain)
            
            # Generate standalone question if not provided
            if not standalone_question:
                try:
                    standalone_question = await generate_standalone_question(
                        query=query,
                        chat_history=session.chat_history,
                        llm=self.llm,
                        custom_prompt=self.config.standalone_question_prompt
                    )
                    logger.info(f"Generated standalone question: {standalone_question}")
                except Exception as e:
                    logger.warning(f"Error generating standalone question: {str(e)}, using original query")
                    standalone_question = query
            
            # Process conversation
            result = await session.conversation.ainvoke({
                "query": query,
                "standalone_question": standalone_question
            })
            
            # Parse response
            response_text = result.get("output_text", "")
            if not response_text and "answer" in result:
                response_text = result["answer"]
            
            # Save to database (async in background)
            session.save_message(query, response_text)
            
            # Update in-memory chat history
            session.chat_history.append((query, response_text))
            if len(session.chat_history) > self.config.max_chat_history:
                session.chat_history = session.chat_history[-self.config.max_chat_history:]
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Save metrics
            try:
                self.id_manager.insert_with_retry("request_metrics", {
                    "user_id": user_id,
                    "request_time": datetime.now(timezone.utc).isoformat(),
                    "response_time": response_time,
                    "success": True,
                    "error_message": None
                })
            except Exception as e:
                logger.error(f"Error saving metrics: {str(e)}")
            
            return {
                "response": response_text,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success",
                "response_time": response_time
            }
            
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            
            # Save error metrics
            try:
                response_time = time.time() - start_time
                self.id_manager.insert_with_retry("request_metrics", {
                    "user_id": user_id,
                    "request_time": datetime.now(timezone.utc).isoformat(),
                    "response_time": response_time,
                    "success": False,
                    "error_message": str(e)
                })
            except Exception as save_error:
                logger.error(f"Error saving error metrics: {str(save_error)}")
            
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e)
            }
