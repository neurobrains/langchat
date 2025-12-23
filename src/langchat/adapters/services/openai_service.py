# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Compatibility module.

Service implementations live under `langchat.adapters.nlpservice.*`.
This namespace is used by tests/docs and remains stable:
  - from langchat.adapters.services.openai_service import OpenAILLMService
"""

from langchat.adapters.nlpservice.openai_service import OpenAILLMService

__all__ = ["OpenAILLMService"]


