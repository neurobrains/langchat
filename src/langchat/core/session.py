# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import warnings
from datetime import datetime, timezone
from typing import Any, List, Tuple, cast

# Fix langchain imports - handle different versions
from langchain.memory import ConversationBufferWindowMemory

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate  # type: ignore

from langchat.adapters.logger import logger

# Suppress warnings before importing langchain
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated.*")


class UserSession:
    """
    Manages user-specific chat sessions with memory and history.
    """

    def __init__(
        self,
        domain: str,
        user_id: str,
        llm: Any,
        vector_adapter: Any,
        reranker_adapter: Any,
        history_store: Any,
        id_manager: Any,
        prompt_template: str | None = None,
        memory_window: int = 20,
        max_chat_history: int = 20,
        retrieval_k: int = 5,
    ):
        """
        Initialize user session.

        Args:
            domain: User domain
            user_id: User ID
            llm: LLM provider instance
            vector_adapter: Vector database adapter
            reranker_adapter: Reranker adapter
            history_store: History storage adapter
            id_manager: ID manager instance
            prompt_template: System prompt template (optional)
            memory_window: Number of messages to keep in memory window
            max_chat_history: Maximum number of chat messages to load from history
            retrieval_k: Number of documents to retrieve from vector DB
        """
        self.domain = domain
        self.user_id = user_id
        self.llm = llm
        self.vector_adapter = vector_adapter
        self.reranker_adapter = reranker_adapter
        self.history_store = history_store
        self.id_manager = id_manager
        self.prompt_template = prompt_template or self._get_default_prompt_template()
        self.memory_window = memory_window
        self.max_chat_history = max_chat_history
        self.retrieval_k = retrieval_k
        self.last_active = datetime.now()

        # Load chat history from database
        self.chat_history = self._load_chat_history()

        # Create user-specific memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            human_prefix="### Input",
            ai_prefix="### Response",
            output_key="answer",
            return_messages=True,
            k=memory_window,
        )

        # Initialize memory with user's chat history
        for query, response in self.chat_history:
            self.memory.save_context({"input": query}, {"answer": response})

        # Create conversation chain
        self.conversation = self._create_conversation()

    def _load_chat_history(self) -> List[Tuple[str, str]]:
        """
        Load chat history from database.

        Returns:
            List of (query, response) tuples
        """
        try:
            response = (
                self.history_store.client.table("chat_history")
                .select("query, response")
                .eq("user_id", self.user_id)
                .eq("domain", self.domain)
                .order("timestamp", desc=True)
                .limit(self.max_chat_history)
                .execute()
            )

            # Extract data from response
            history = [
                (cast("str", item.get("query", "")), cast("str", item.get("response", "")))
                for item in response.data
                if isinstance(item, dict)
            ]

            # Return history in chronological order
            return history[::-1]
        except Exception as e:
            logger.error(f"Error loading chat history: {str(e)}")
            return []

    def save_message(self, query: str, response: str):
        """
        Save message to database.

        Args:
            query: User query
            response: AI response
        """
        try:
            logger.info(f"Attempting to save message for user {self.user_id}, domain {self.domain}")
            result = self.id_manager.insert_with_retry(
                "chat_history",
                {
                    "user_id": self.user_id,
                    "domain": self.domain,
                    "query": query,
                    "response": response,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            if result is not None:
                logger.info("Message saved successfully to database")
            else:
                logger.error("Failed to save message to database after retries")
        except Exception as e:
            logger.error(f"Error saving message to Supabase: {str(e)}", exc_info=True)

    def _get_default_prompt_template(self) -> str:
        """Get default prompt template."""
        return """You are a highly skilled AI assistant with access to relevant documentation and past conversations.

Your task is to provide accurate, helpful, and contextually aware responses.

### Context from Retrieved Documents:
{context}

### Conversation History:
{chat_history}

### User's Question:
{query}

### Instructions:
1. Use information from both the context and conversation history
2. If the answer isn't in the provided context, say so clearly
3. Be concise but thorough
4. Maintain conversation continuity

### Response:"""

    def _create_conversation(self):
        """
        Create conversation chain with retrieval and memory.

        Returns:
            CustomConversationChain instance
        """
        try:
            # Get retriever from vector adapter
            base_retriever = self.vector_adapter.get_retriever(k=self.retrieval_k)

            # Create compression retriever with reranker
            compression_retriever = self.reranker_adapter.create_compression_retriever(
                base_retriever
            )

            # Create a simple retrieval QA chain wrapper
            # We'll handle the document combination manually in CustomConversationChain
            retrieval_qa = SimpleRetrievalQA(
                retriever=compression_retriever,
                llm=self.llm.current_llm,
                prompt_template=self.prompt_template,
                verbose_chains=False,
            )

            # Wrap in custom conversation chain
            return CustomConversationChain(retrieval_qa, self.memory, self.chat_history)

        except Exception as e:
            logger.error(f"Error creating conversation chain for user {self.user_id}: {str(e)}")
            raise


class SimpleRetrievalQA:
    """
    Simple retrieval QA wrapper that handles document retrieval.
    """

    def __init__(self, retriever, llm, prompt_template: str, verbose_chains: bool = False):
        self.retriever = retriever
        self.llm = llm
        self.prompt_template = prompt_template
        self.verbose_chains = verbose_chains


class CustomConversationChain:
    """
    Custom conversation chain that handles memory and formatting.
    """

    def __init__(
        self,
        retrieval_qa,
        memory: ConversationBufferWindowMemory,
        session_chat_history=None,
    ):
        """
        Initialize custom conversation chain.

        Args:
            retrieval_qa: SimpleRetrievalQA instance
            memory: Conversation memory
            session_chat_history: Reference to the session's chat_history list (not a copy)
        """
        self.retrieval_qa = retrieval_qa
        self.memory = memory
        # Store a direct reference to the session's chat_history list (not a copy)
        # This ensures updates to the session's chat_history are reflected here
        self.session_chat_history = session_chat_history if session_chat_history is not None else []

    async def ainvoke(self, inputs: dict):
        """
        Invoke the conversation chain asynchronously.

        Args:
            inputs: Dictionary with 'query' and optionally 'standalone_question'

        Returns:
            Result dictionary with 'output_text' or 'answer'
        """
        query = inputs.get("query", "")
        standalone_question = inputs.get("standalone_question", query)

        # Use session chat_history directly (more reliable than memory)
        # Format chat history from session chat_history list
        # IMPORTANT: Use the current session_chat_history (it's a reference, so it's always up-to-date)
        # But exclude the current query/response if it's already been added
        chat_history_to_use = self.session_chat_history if self.session_chat_history else []

        # Format the chat history
        if chat_history_to_use:
            formatted_chat_history = "\n".join(
                [f"Human: {q}\nAssistant: {a}" for q, a in chat_history_to_use]
            )
        else:
            # Fallback to memory if session chat_history is empty
            memory_vars = self.memory.load_memory_variables({})
            chat_history_messages = memory_vars.get("chat_history", "")

            # Format chat history properly for the prompt
            formatted_chat_history = ""
            if chat_history_messages:
                if isinstance(chat_history_messages, list) and hasattr(
                    chat_history_messages[0], "content"
                ):
                    pairs = []
                    for i in range(0, len(chat_history_messages), 2):
                        if i + 1 < len(chat_history_messages):
                            human = chat_history_messages[i].content
                            ai = chat_history_messages[i + 1].content
                            pairs.append(f"Human: {human}\nAssistant: {ai}")
                    formatted_chat_history = "\n".join(pairs)
                else:
                    formatted_chat_history = str(chat_history_messages)

        # Show verbose output if enabled (to debug chat_history)
        if hasattr(self.retrieval_qa, "verbose_chains") and self.retrieval_qa.verbose_chains:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()
            console.print()
            console.print(
                Panel(
                    f"Using session chat_history: {len(self.session_chat_history)} entries\n\nFormatted Chat History:\n{formatted_chat_history}",
                    title="[bold blue]MAIN CHAIN - Chat History Debug[/bold blue]",
                    title_align="left",
                    border_style="blue",
                    padding=(1, 2),
                )
            )
            console.print()

        # Get relevant documents using the newer invoke method
        try:
            # Try using the newer invoke method first
            docs = self.retrieval_qa.retriever.invoke(standalone_question)
        except AttributeError:
            # Fallback to deprecated method if invoke doesn't exist
            docs = self.retrieval_qa.retriever.get_relevant_documents(standalone_question)

        # Combine documents into context
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create prompt with all required variables
        prompt = PromptTemplate(
            template=self.retrieval_qa.prompt_template,
            input_variables=["context", "question", "chat_history"],
        )

        # Format the prompt
        formatted_prompt = prompt.format(
            context=context, question=query, chat_history=formatted_chat_history
        )

        # Show verbose output if enabled (to debug chat_history)
        if hasattr(self.retrieval_qa, "verbose_chains") and self.retrieval_qa.verbose_chains:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()
            console.print()
            console.print(
                Panel(
                    formatted_prompt,
                    title="[bold green]MAIN CHAIN - Formatted Prompt (with context, chat_history, and question)[/bold green]",
                    title_align="left",
                    border_style="green",
                    padding=(1, 2),
                )
            )
            console.print()

        # Call LLM with the formatted prompt as a message
        # ChatOpenAI expects a list of messages or a string
        try:
            from langchain_core.messages import HumanMessage
        except ImportError:
            from langchain.schema import HumanMessage

        # Create a message with the formatted prompt
        messages = [HumanMessage(content=formatted_prompt)]
        result = await self.retrieval_qa.llm.ainvoke(messages)

        # Extract response text with better handling
        response_text = ""
        if hasattr(result, "content"):
            response_text = result.content
            if isinstance(response_text, list):
                # Handle case where content is a list
                response_text = " ".join(str(item) for item in response_text)
        elif isinstance(result, str):
            response_text = result
        elif hasattr(result, "text"):
            response_text = result.text
        else:
            response_text = str(result)

        # Ensure response is not empty and is a string
        if not response_text or not isinstance(response_text, str):
            logger.warning(f"Invalid response from LLM: {type(result)} - {result}")
            response_text = "I apologize, but I didn't receive a valid response. Please try again."
        else:
            response_text = response_text.strip()

        # Save the interaction to memory
        self.memory.save_context({"input": query}, {"answer": response_text})

        return {
            "output_text": response_text,
            "answer": response_text,
            "source_documents": docs,
        }
