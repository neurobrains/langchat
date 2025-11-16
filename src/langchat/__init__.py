"""
LangChat - A conversational AI library with vector search capabilities.
"""

__version__ = "0.0.3"

from langchat.config import LangChatConfig
from langchat.core.engine import LangChatEngine
from langchat.core.session import UserSession
from langchat.exceptions import UnsupportedFileTypeError
from langchat.main import LangChat
from langchat.utils.document_indexer import DocumentIndexer

__all__ = [
    "LangChat",
    "LangChatEngine",
    "UserSession",
    "LangChatConfig",
    "DocumentIndexer",
    "UnsupportedFileTypeError",
]
