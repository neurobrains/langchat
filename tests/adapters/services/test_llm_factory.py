# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from langchat.adapters.services.anthropic_service import AnthropicLLMService
from langchat.adapters.services.factory import create_llm_service
from langchat.adapters.services.gemini_service import GeminiLLMService
from langchat.adapters.services.openai_service import OpenAILLMService
from langchat.config import LangChatConfig


def test_llm_factory_openai_explicit():
    cfg = LangChatConfig(
        llm_provider="openai",
        openai_api_keys=["k1"],
    )
    llm = create_llm_service(cfg)
    assert isinstance(llm, OpenAILLMService)


def test_llm_factory_gemini_explicit():
    cfg = LangChatConfig(
        llm_provider="gemini",
        gemini_api_keys=["g1"],
    )
    llm = create_llm_service(cfg)
    assert isinstance(llm, GeminiLLMService)


def test_llm_factory_anthropic_explicit():
    cfg = LangChatConfig(
        llm_provider="anthropic",
        anthropic_api_keys=["a1"],
    )
    llm = create_llm_service(cfg)
    assert isinstance(llm, AnthropicLLMService)


def test_llm_factory_auto_prefers_openai_when_present():
    cfg = LangChatConfig(
        llm_provider="auto",
        openai_api_keys=["k1"],
        gemini_api_keys=["g1"],
        anthropic_api_keys=["a1"],
    )
    llm = create_llm_service(cfg)
    assert isinstance(llm, OpenAILLMService)


