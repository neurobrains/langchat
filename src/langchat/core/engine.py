"""
LangChat Engine - Main entry point for using LangChat.
"""

import asyncio
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel

from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter
from langchat.adapters.services.openai_service import OpenAILLMService
from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter
from langchat.config import LangChatConfig
from langchat.core.prompts import generate_standalone_question
from langchat.core.session import UserSession
from langchat.logger import logger

# Global flag to track if running as API server
_is_api_server_mode = False


def set_api_server_mode(enabled: bool = True):
    """Set API server mode flag to disable console panel output."""
    global _is_api_server_mode
    _is_api_server_mode = enabled


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
        if config is None:
            self.config = LangChatConfig.from_env()
        else:
            self.config = config

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
                self.config.supabase_url, self.config.supabase_key
            )
        else:
            raise ValueError("Supabase URL and key must be provided")

        # Initialize ID manager
        self.id_manager = IDManager(self.supabase_adapter.client, initial_value=0, retry_attempts=5)

        # Initialize LLM service (OpenAI)
        if not self.config.openai_api_keys:
            raise ValueError("OpenAI API keys must be provided")
        self.llm = OpenAILLMService(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            api_keys=self.config.openai_api_keys,
            max_retries_per_key=self.config.max_llm_retries,
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
            embedding_api_key=embedding_api_key,
        )
        logger.info(f"Successfully connected to Pinecone index: {self.config.pinecone_index_name}")

        # Initialize Flashrank reranker
        # Use config's reranker_cache_dir (relative to current working directory)
        reranker_cache_dir = Path(self.config.reranker_cache_dir)
        reranker_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Reranker cache directory created/verified: {reranker_cache_dir}")

        # Initialize ranker (this will download the model if not already present)
        self.reranker_adapter = FlashrankRerankAdapter(
            model_name=self.config.reranker_model,
            cache_dir=reranker_cache_dir,
            top_n=self.config.reranker_top_n,
        )
        logger.info(f"Reranker model '{self.config.reranker_model}' initialized")

    def _initialize_database(self):
        """Initialize database tables."""
        try:
            # First, try to create tables if they don't exist
            logger.info("Checking database tables...")
            tables_created = self.supabase_adapter.create_tables_if_not_exist()

            if not tables_created:
                # If automatic creation failed, try to check if tables exist anyway
                # (they might have been created manually)
                try:
                    self.supabase_adapter.client.table("chat_history").select("id").limit(
                        1
                    ).execute()
                    self.supabase_adapter.client.table("request_metrics").select("id").limit(
                        1
                    ).execute()
                    logger.info("Database tables exist (created manually)")
                except Exception as e:
                    error_str = str(e).lower()
                    if "pgrst205" in error_str or "could not find the table" in error_str:
                        logger.error(
                            "Tables do not exist and could not be created automatically. "
                            "Please create them manually using the SQL provided in the logs above, "
                            "or use a service role key for automatic creation."
                        )
                        # Don't raise - allow the app to continue, but operations will fail
                        return
                    else:
                        # Some other error
                        logger.warning(f"Error checking tables: {str(e)}")

            # Always initialize ID Manager early to prevent initialization during save
            # This ensures counters are set up before any inserts happen
            if not self.id_manager.initialized:
                self.id_manager.initialize()

            logger.info("Database connection successful")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            # Try to initialize ID manager anyway (with default values)
            if not self.id_manager.initialized:
                try:
                    self.id_manager.initialize()
                except Exception as init_error:
                    logger.error(f"Error initializing ID Manager: {str(init_error)}")

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
            prompt_template = (
                self.config.system_prompt_template or self.config.get_default_prompt_template()
            )

            self.sessions[session_key] = UserSession(
                domain=domain,
                user_id=user_id,
                config=self.config,
                llm=self.llm,
                vector_adapter=self.vector_adapter,
                reranker_adapter=self.reranker_adapter,
                supabase_adapter=self.supabase_adapter,
                id_manager=self.id_manager,
                prompt_template=prompt_template,
            )

        return self.sessions[session_key]

    async def chat(
        self,
        query: str,
        user_id: str,
        domain: str = "default",
        standalone_question: Optional[str] = None,
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
                        custom_prompt=self.config.standalone_question_prompt,
                        verbose_chains=self.config.verbose_chains,
                    )
                    logger.info(f"Generated standalone question: {standalone_question}")
                except Exception as e:
                    logger.warning(
                        f"Error generating standalone question: {str(e)}, using original query"
                    )
                    standalone_question = query

            # Process conversation
            result = await session.conversation.ainvoke(
                {"query": query, "standalone_question": standalone_question}
            )

            # Parse response
            response_text = result.get("output_text", "")
            if not response_text and "answer" in result:
                response_text = result["answer"]

            # Print formatted response to console with better styling
            # Show panel unless running in API server mode
            if not _is_api_server_mode:
                try:
                    console = Console(force_terminal=True)
                    console.print()  # Empty line for spacing
                    console.print(
                        Panel(
                            response_text,
                            title="[bold cyan]Response[/bold cyan]",
                            title_align="left",
                            border_style="cyan",
                            padding=(1, 2),
                        )
                    )
                    console.print()  # Empty line for spacing
                except Exception as e:
                    # Fallback if Rich console fails
                    logger.warning(f"Could not display Rich panel: {str(e)}")

            # Save to database in background (non-blocking for faster response)
            # Use asyncio event loop executor for proper async integration
            async def save_message_background():
                """Background async task to save message"""
                try:
                    # Get event loop and run sync save_message in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, session.save_message, query, response_text)
                except Exception as e:
                    logger.error(f"Exception in save_message_background: {str(e)}", exc_info=True)

            # Create task to run in background (fire and forget for performance)
            try:
                # Schedule the save task
                # Store task reference to prevent garbage collection issues
                # The task will complete in background
                asyncio.create_task(save_message_background())
            except RuntimeError:
                # Fallback if no event loop is running (shouldn't happen in async context)
                # Use thread as fallback
                def save_in_thread():
                    try:
                        session.save_message(query, response_text)
                    except Exception as e:
                        logger.error(f"Exception in save_in_thread: {str(e)}", exc_info=True)

                threading.Thread(
                    target=save_in_thread, daemon=False, name="save-message-thread"
                ).start()
            except Exception as e:
                logger.error(f"Error scheduling save_message task: {str(e)}", exc_info=True)
                # Last resort: try direct save (will block but ensures save)
                try:
                    session.save_message(query, response_text)
                except Exception as save_error:
                    logger.error(
                        f"Error in direct save_message: {str(save_error)}",
                        exc_info=True,
                    )

            # Update in-memory chat history
            session.chat_history.append((query, response_text))
            if len(session.chat_history) > self.config.max_chat_history:
                # Modify list in place to preserve reference (don't reassign)
                # This ensures CustomConversationChain still has a valid reference
                excess = len(session.chat_history) - self.config.max_chat_history
                del session.chat_history[:excess]

            # Calculate response time
            response_time = time.time() - start_time

            # Save metrics in background (non-blocking - don't wait for it)
            def save_metrics_background():
                try:
                    self.id_manager.insert_with_retry(
                        "request_metrics",
                        {
                            "user_id": user_id,
                            "request_time": datetime.now(timezone.utc).isoformat(),
                            "response_time": response_time,
                            "success": True,
                            "error_message": None,
                        },
                    )
                except Exception as e:
                    logger.error(f"Error saving metrics: {str(e)}")

            threading.Thread(target=save_metrics_background, daemon=True).start()

            return {
                "response": response_text,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success",
                "response_time": response_time,
            }

        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")

            # Save error metrics in background (non-blocking)
            response_time = time.time() - start_time
            error_message = str(e)

            def save_error_metrics_background():
                try:
                    self.id_manager.insert_with_retry(
                        "request_metrics",
                        {
                            "user_id": user_id,
                            "request_time": datetime.now(timezone.utc).isoformat(),
                            "response_time": response_time,
                            "success": False,
                            "error_message": error_message,
                        },
                    )
                except Exception as save_error:
                    logger.error(f"Error saving error metrics: {str(save_error)}")

            threading.Thread(target=save_error_metrics_background, daemon=True).start()

            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e),
            }
