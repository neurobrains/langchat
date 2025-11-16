"""
Configuration module for LangChat.
All settings can be customized by developers.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pytz


@dataclass
class LangChatConfig:
    """
    Configuration class for LangChat library.
    Developers can customize all settings here.
    """

    # OpenAI Configuration
    openai_api_keys: List[str]
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 1.0
    openai_embedding_model: str = "text-embedding-3-large"

    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None  # Must be configured

    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # Vector Search Configuration
    retrieval_k: int = 5  # Number of documents to retrieve
    reranker_top_n: int = 3  # Top N results after reranking
    reranker_model: str = "ms-marco-MiniLM-L-12-v2"
    reranker_cache_dir: str = "rerank_models"

    # Session Configuration
    max_chat_history: int = 20  # Maximum messages to keep in memory
    memory_window: int = 20  # Conversation buffer window size

    # Timezone Configuration
    timezone: str = "Asia/Dhaka"

    # Prompt Configuration
    system_prompt_template: Optional[str] = None
    standalone_question_prompt: Optional[str] = None  # Custom standalone question prompt

    # LLM Retry Configuration
    max_llm_retries: int = 2  # Retry count per API key

    # Server Configuration
    server_port: int = 8000

    # Output Configuration
    verbose_chains: bool = False  # Show LangChain verbose output for debugging chains

    @classmethod
    def from_env(cls) -> "LangChatConfig":
        """
        Create configuration from environment variables.
        """
        openai_keys_str = os.getenv("OPENAI_API_KEYS", "")
        openai_keys = [k.strip() for k in openai_keys_str.split(",") if k.strip()]

        # Fallback to single key if list not provided
        if not openai_keys:
            single_key = os.getenv("OPENAI_API_KEY")
            if single_key:
                openai_keys = [single_key]

        return cls(
            openai_api_keys=openai_keys,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "1.0")),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", "abroad-inquiry-json-qa"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "5")),
            reranker_top_n=int(os.getenv("RERANKER_TOP_N", "3")),
            reranker_model=os.getenv("RERANKER_MODEL", "ms-marco-MiniLM-L-12-v2"),
            reranker_cache_dir=os.getenv("RERANKER_CACHE_DIR", "rerank_models"),
            max_chat_history=int(os.getenv("MAX_CHAT_HISTORY", "20")),
            memory_window=int(os.getenv("MEMORY_WINDOW", "20")),
            timezone=os.getenv("TIMEZONE", "Asia/Dhaka"),
            server_port=int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000"))),
            verbose_chains=os.getenv("VERBOSE_CHAINS", "false").lower() in ("true", "1", "yes"),
        )

    def get_formatted_time(self) -> str:
        """
        Get current formatted time based on configured timezone.
        """
        tz = pytz.timezone(self.timezone)
        bd_time = datetime.now(tz)
        return bd_time.strftime("%A, %d %B %Y")

    def get_default_prompt_template(self) -> str:
        """
        Get default system prompt template.
        """
        # Simple template - use {{context}}, {{chat_history}}, {{question}} as placeholders for PromptTemplate
        template = """You are a helpful assistant. Answer correctly the user question.

Use the following context and chat history to answer:

Context:
{{context}}

Current conversation:
{{chat_history}}

Human: {{question}}
AI Assistant:"""

        return template
