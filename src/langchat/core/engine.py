# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import asyncio
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from langchat.adapters.database.id_manager import IDManager
from langchat.adapters.logger import logger
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter
from langchat.core.prompts import generate_standalone_question
from langchat.core.session import UserSession

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

    def __init__(
        self,
        *,
        llm=None,
        vector_db=None,
        db=None,
        reranker=None,
        prompt_template: Optional[str] = None,
        standalone_question_prompt: Optional[str] = None,
        verbose: Optional[bool] = False,
        max_chat_history: int = 20,
    ):
        """
        Initialize LangChat engine.

        Args:
            llm: LLM provider instance (required)
            vector_db: Vector database adapter (required)
            db: Database adapter for history storage (required)
            reranker: Reranker adapter (optional, defaults to FlashrankRerankAdapter)
            prompt_template: System prompt template (optional)
            standalone_question_prompt: Standalone question prompt (optional)
            verbose: Enable verbose logging (default: False)
            max_chat_history: Maximum chat history to keep (default: 20)
        """
        if llm is None:
            raise ValueError("LLM provider is required")
        if vector_db is None:
            raise ValueError("Vector database adapter is required")
        if db is None:
            raise ValueError("Database adapter is required")

        self.llm = llm
        self.vector_adapter = vector_db
        self.history_store = db
        self.reranker_adapter = reranker or FlashrankRerankAdapter(
            model_name="ms-marco-MiniLM-L-12-v2",
            cache_dir="rerank_models",
            top_n=3,
        )

        # Internal state
        self.sessions: dict[str, UserSession] = {}
        self.id_manager = IDManager(self.history_store.client)

        # Prompts / behavior
        self.prompt_template = prompt_template or self._get_default_prompt_template()
        self.standalone_question_prompt = standalone_question_prompt
        self.verbose = verbose or False

        # Session tuning
        self.max_chat_history = max_chat_history

    def _get_default_prompt_template(self) -> str:
        """Get default prompt template."""
        return """You are a helpful AI assistant. Answer questions clearly and accurately.

Use the following context to answer:
{context}

Previous conversation:
{chat_history}

User question: {question}

Your response:"""

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
            self.sessions[session_key] = UserSession(
                domain=domain,
                user_id=user_id,
                llm=self.llm,
                vector_adapter=self.vector_adapter,
                reranker_adapter=self.reranker_adapter,
                history_store=self.history_store,
                id_manager=self.id_manager,
                prompt_template=self.prompt_template,
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
                        custom_prompt=self.standalone_question_prompt,
                        verbose_chains=self.verbose,
                        llm=self.llm,
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

            # Validate response
            if not response_text or len(response_text.strip()) < 1:
                logger.warning("Empty or invalid response received from LLM")
                response_text = (
                    "I apologize, but I didn't receive a valid response. Please try again."
                )
            elif len(response_text.strip()) < 3:
                logger.warning(
                    f"Response too short: '{response_text}'. This might indicate an issue with the LLM."
                )

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
            if len(session.chat_history) > self.max_chat_history:
                # Modify list in place to preserve reference (don't reassign)
                # This ensures CustomConversationChain still has a valid reference
                excess = len(session.chat_history) - self.max_chat_history
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
