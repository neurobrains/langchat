"""
User session management for LangChat.
"""

import logging
from typing import List, Tuple, Optional
from datetime import datetime, timezone
# Fix langchain imports - handle different versions
from langchain.memory import ConversationBufferWindowMemory

from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter
from langchat.adapters.supabase.id_manager import IDManager
from langchat.adapters.services.openai_service import OpenAILLMService
from langchat.adapters.vector_db.pinecone_adapter import PineconeVectorAdapter
from langchat.adapters.reranker.flashrank_adapter import FlashrankRerankAdapter
from langchat.config import LangChatConfig

logger = logging.getLogger(__name__)


class UserSession:
    """
    Manages user-specific chat sessions with memory and history.
    """
    
    def __init__(
        self,
        domain: str,
        user_id: str,
        config: LangChatConfig,
        llm: OpenAILLMService,
        vector_adapter: PineconeVectorAdapter,
        reranker_adapter: FlashrankRerankAdapter,
        supabase_adapter: SupabaseAdapter,
        id_manager: IDManager,
        prompt_template: str
    ):
        """
        Initialize user session.
        
        Args:
            domain: User domain
            user_id: User ID
            config: LangChat configuration
            llm: LLM provider instance
            vector_adapter: Vector database adapter
            reranker_adapter: Reranker adapter
            supabase_adapter: Supabase database adapter
            id_manager: ID manager instance
            prompt_template: System prompt template
        """
        self.domain = domain
        self.user_id = user_id
        self.config = config
        self.llm = llm
        self.vector_adapter = vector_adapter
        self.reranker_adapter = reranker_adapter
        self.supabase_adapter = supabase_adapter
        self.id_manager = id_manager
        self.prompt_template = prompt_template
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
            k=config.memory_window
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
            response = self.supabase_adapter.client.table("chat_history") \
                .select("query, response") \
                .eq("user_id", self.user_id) \
                .eq("domain", self.domain) \
                .order("timestamp", desc=True) \
                .limit(self.config.max_chat_history) \
                .execute()
            
            # Extract data from response
            history = [(item["query"], item["response"]) for item in response.data]
            
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
            self.id_manager.insert_with_retry("chat_history", {
                "user_id": self.user_id,
                "domain": self.domain,
                "query": query,
                "response": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Error saving message to Supabase: {str(e)}")
    
    def _create_conversation(self):
        """
        Create conversation chain with retrieval and memory.
        
        Returns:
            CustomConversationChain instance
        """
        try:
            # Create prompt template
            prompt = PromptTemplate(
                input_variables=["context", "question", "chat_history"],
                template=self.prompt_template
            )
            
            # Create QA chain - OpenAI service
            llm_instance = self.llm.current_llm
            
            qa_chain = load_qa_chain(
                llm=llm_instance,
                chain_type="stuff",
                prompt=prompt,
                verbose=True
            )
            
            # Get retriever from vector adapter
            base_retriever = self.vector_adapter.get_retriever(k=self.config.retrieval_k)
            
            # Create compression retriever with reranker
            compression_retriever = self.reranker_adapter.create_compression_retriever(base_retriever)
            
            # Create retrieval QA chain
            retrieval_qa = RetrievalQA(
                combine_documents_chain=qa_chain,
                retriever=compression_retriever,
                return_source_documents=True,
                verbose=True
            )
            
            # Wrap in custom conversation chain
            return CustomConversationChain(retrieval_qa, self.memory)
            
        except Exception as e:
            logger.error(f"Error creating conversation chain for user {self.user_id}: {str(e)}")
            raise


class CustomConversationChain:
    """
    Custom conversation chain that handles memory and formatting.
    """
    
    def __init__(self, retrieval_qa: RetrievalQA, memory: ConversationBufferWindowMemory):
        """
        Initialize custom conversation chain.
        
        Args:
            retrieval_qa: Retrieval QA chain
            memory: Conversation memory
        """
        self.retrieval_qa = retrieval_qa
        self.memory = memory
    
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
        
        # Get memory variables (chat history)
        memory_vars = self.memory.load_memory_variables({})
        chat_history_messages = memory_vars.get("chat_history", "")
        
        # Format chat history properly for the prompt
        formatted_chat_history = ""
        if chat_history_messages:
            if isinstance(chat_history_messages, list) and hasattr(chat_history_messages[0], 'content'):
                pairs = []
                for i in range(0, len(chat_history_messages), 2):
                    if i + 1 < len(chat_history_messages):
                        human = chat_history_messages[i].content
                        ai = chat_history_messages[i + 1].content
                        pairs.append(f"Human: {human}\nAssistant: {ai}")
                formatted_chat_history = "\n".join(pairs)
            else:
                formatted_chat_history = str(chat_history_messages)
        
        # Get relevant documents
        docs = self.retrieval_qa.retriever.get_relevant_documents(standalone_question)
        
        # Prepare inputs for the QA chain
        qa_inputs = {
            "input_documents": docs,
            "question": query,
            "context": "\n\n".join([doc.page_content for doc in docs]),
            "chat_history": formatted_chat_history
        }
        
        # Run the QA chain
        result = await self.retrieval_qa.combine_documents_chain.ainvoke(qa_inputs)
        
        # Extract response text
        response_text = result.get("output_text", "")
        if not response_text and "answer" in result:
            response_text = result["answer"]
        
        # Save the interaction to memory
        self.memory.save_context({"input": query}, {"answer": response_text})
        
        return result
