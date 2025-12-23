# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Compatibility module.

Service implementations live under `langchat.adapters.nlpservice.*`.
This namespace is used by tests/docs and remains stable:
  - from langchat.adapters.services.anthropic_service import AnthropicLLMService
"""

from langchat.adapters.nlpservice.anthropic_service import AnthropicLLMService

__all__ = ["AnthropicLLMService"]


