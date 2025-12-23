# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
LangChat public API.

Keep imports here stable so users can do:
  - from langchat import LangChat, LangChatConfig
  - from langchat.api import create_app
"""

from langchat.core.config import LangChatConfig
from langchat.sdk import LangChat

__all__ = [
    "LangChat",
    "LangChatConfig",
]


