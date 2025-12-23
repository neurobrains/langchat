# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Compatibility module.

Service implementations live under `langchat.adapters.nlpservice.*`.
This namespace is used by tests/docs and remains stable:
  - from langchat.adapters.services.gemini_service import GeminiLLMService
"""

from langchat.adapters.nlpservice.gemini_service import GeminiLLMService

__all__ = ["GeminiLLMService"]


