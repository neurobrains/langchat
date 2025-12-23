# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime

import pytz


@dataclass
class LangChatConfig:
    """
    Configuration class for LangChat library.
    Developers can customize all settings here.
    """

    # LLM Provider Selection
    # - "auto" (default): detect based on env keys
    # - "openai" | "gemini" | "anthropic"
    llm_provider: str = "auto"

    # OpenAI Configuration
    openai_api_keys: list[str] = field(default_factory=list)
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 1.0
    openai_embedding_model: str = "text-embedding-3-large"

    # Gemini Configuration
    gemini_api_keys: list[str] = field(default_factory=list)
    gemini_model: str = "gemini-1.5-flash"
    gemini_temperature: float = 1.0

    # Anthropic Configuration
    anthropic_api_keys: list[str] = field(default_factory=list)
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 1.0

    # Pinecone Configuration
    pinecone_api_key: str | None = None
    pinecone_index_name: str | None = None  # Must be configured

    # Supabase Configuration
    supabase_url: str | None = None
    supabase_key: str | None = None

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
    system_prompt_template: str | None = None
    standalone_question_prompt: str | None = None  # Custom standalone question prompt

    # LLM Retry Configuration
    max_llm_retries: int = 2  # Retry count per API key

    # Server Configuration
    server_port: int = 8000

    # Output Configuration
    verbose_chains: bool = False  # Show LangChain verbose output for debugging chains

    @classmethod
    def from_env(cls) -> LangChatConfig:
        """
        Create configuration from environment variables.
        """
        llm_provider = os.getenv("LANGCHAT_LLM_PROVIDER", "auto").strip().lower() or "auto"

        openai_keys_str = os.getenv("OPENAI_API_KEYS", "")
        openai_keys = [k.strip() for k in openai_keys_str.split(",") if k.strip()]

        # Fallback to single key if list not provided
        if not openai_keys:
            single_key = os.getenv("OPENAI_API_KEY")
            if single_key:
                openai_keys = [single_key]

        gemini_keys_str = os.getenv("GEMINI_API_KEYS", "")
        gemini_keys = [k.strip() for k in gemini_keys_str.split(",") if k.strip()]
        if not gemini_keys:
            single_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if single_key:
                gemini_keys = [single_key]

        anthropic_keys_str = os.getenv("ANTHROPIC_API_KEYS", "")
        anthropic_keys = [k.strip() for k in anthropic_keys_str.split(",") if k.strip()]
        if not anthropic_keys:
            single_key = os.getenv("ANTHROPIC_API_KEY")
            if single_key:
                anthropic_keys = [single_key]

        return cls(
            llm_provider=llm_provider,
            openai_api_keys=openai_keys,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "1.0")),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            gemini_api_keys=gemini_keys,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "1.0")),
            anthropic_api_keys=anthropic_keys,
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            anthropic_temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "1.0")),
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
        template = """You are a helpful assistant. Answer correctly the user question.

        Use the following context and chat history to answer:

        Context:
        {{context}}

        Current conversation:
        {{chat_history}}

        Human: {{question}}
        AI Assistant:"""

        return template


__all__ = ["LangChatConfig"]


