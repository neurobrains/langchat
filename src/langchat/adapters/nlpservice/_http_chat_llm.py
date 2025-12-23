"""
Compatibility wrapper.

The HTTP chat LLM helper now lives in `langchat.adapters.services._http_chat_llm`.
"""

from langchat.adapters.services._http_chat_llm import (  # noqa: F401
    HTTPChatLLM,
    SimpleAIMessage,
    _messages_to_text,
    post_json,
)
