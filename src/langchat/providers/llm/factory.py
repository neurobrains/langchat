# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""LLM Provider Factory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langchat.core.config import LangChatConfig


def create_llm_provider(
    provider: str = "auto",
    config: LangChatConfig | None = None,
    **kwargs: Any
) -> Any:
    """
    Create an LLM provider based on provider name or config.

    Args:
        provider: Provider name ("auto", "openai", "gemini", "anthropic", "ollama", "cohere", "mistral")
        config: LangChatConfig instance (for auto-detection)
        **kwargs: Additional provider-specific arguments

    Returns:
        LLM provider instance

    Example:
        ```python
        # Auto-detect from config
        llm = create_llm_provider("auto", config=config)

        # Specify provider explicitly
        llm = create_llm_provider("openai", api_keys=["sk-..."], model="gpt-4")

        # Ollama (local)
        llm = create_llm_provider("ollama", model="llama2", base_url="http://localhost:11434")
        ```
    """
    from langchat.providers.llm.anthropic_provider import AnthropicProvider
    from langchat.providers.llm.cohere_provider import CohereProvider
    from langchat.providers.llm.gemini_provider import GeminiProvider
    from langchat.providers.llm.mistral_provider import MistralProvider
    from langchat.providers.llm.ollama_provider import OllamaProvider
    from langchat.providers.llm.openai_provider import OpenAIProvider

    provider = provider.strip().lower()

    # Auto-detect from config
    if provider == "auto":
        if not config:
            raise ValueError("Config is required for auto provider detection")

        if config.openai_api_keys:
            provider = "openai"
        elif config.gemini_api_keys:
            provider = "gemini"
        elif config.anthropic_api_keys:
            provider = "anthropic"
        else:
            raise ValueError(
                "No API keys found. Set OPENAI_API_KEY(S), GEMINI_API_KEY(S), "
                "ANTHROPIC_API_KEY(S), COHERE_API_KEY(S), MISTRAL_API_KEY(S), "
                "or configure Ollama for local models"
            )

    # Create provider
    if provider == "openai":
        api_keys = kwargs.get("api_keys") or (config.openai_api_keys if config else None)
        model = kwargs.get("model") or (config.openai_model if config else "gpt-4o-mini")
        temperature = kwargs.get("temperature") or (config.openai_temperature if config else 1.0)
        max_retries = kwargs.get("max_retries_per_key") or (config.max_llm_retries if config else 2)

        return OpenAIProvider(
            model=model,
            temperature=temperature,
            api_keys=api_keys,
            max_retries_per_key=max_retries,
        )

    elif provider == "gemini":
        api_keys = kwargs.get("api_keys") or (config.gemini_api_keys if config else None)
        model = kwargs.get("model") or (config.gemini_model if config else "gemini-1.5-flash")
        temperature = kwargs.get("temperature") or (config.gemini_temperature if config else 1.0)
        max_retries = kwargs.get("max_retries_per_key") or (config.max_llm_retries if config else 2)

        return GeminiProvider(
            model=model,
            temperature=temperature,
            api_keys=api_keys,
            max_retries_per_key=max_retries,
        )

    elif provider == "anthropic":
        api_keys = kwargs.get("api_keys") or (config.anthropic_api_keys if config else None)
        model = kwargs.get("model") or (config.anthropic_model if config else "claude-3-5-sonnet-20241022")
        temperature = kwargs.get("temperature") or (config.anthropic_temperature if config else 1.0)
        max_retries = kwargs.get("max_retries_per_key") or (config.max_llm_retries if config else 2)
        max_tokens = kwargs.get("max_tokens", 4096)

        return AnthropicProvider(
            model=model,
            temperature=temperature,
            api_keys=api_keys,
            max_retries_per_key=max_retries,
            max_tokens=max_tokens,
        )

    elif provider == "ollama":
        model = kwargs.get("model", "llama2")
        temperature = kwargs.get("temperature", 0.7)
        base_url = kwargs.get("base_url", "http://localhost:11434")
        options = kwargs.get("options")

        return OllamaProvider(
            model=model,
            temperature=temperature,
            base_url=base_url,
            options=options,
        )

    elif provider == "cohere":
        api_keys = kwargs.get("api_keys")
        if not api_keys and config and hasattr(config, "cohere_api_keys"):
            api_keys = config.cohere_api_keys

        model = kwargs.get("model", "command")
        temperature = kwargs.get("temperature", 0.7)
        max_retries = kwargs.get("max_retries_per_key", 2)
        max_tokens = kwargs.get("max_tokens", 4096)

        return CohereProvider(
            model=model,
            temperature=temperature,
            api_keys=api_keys,
            max_retries_per_key=max_retries,
            max_tokens=max_tokens,
        )

    elif provider == "mistral":
        api_keys = kwargs.get("api_keys")
        if not api_keys and config and hasattr(config, "mistral_api_keys"):
            api_keys = config.mistral_api_keys

        model = kwargs.get("model", "mistral-small-latest")
        temperature = kwargs.get("temperature", 0.7)
        max_retries = kwargs.get("max_retries_per_key", 2)
        max_tokens = kwargs.get("max_tokens", 4096)

        return MistralProvider(
            model=model,
            temperature=temperature,
            api_keys=api_keys,
            max_retries_per_key=max_retries,
            max_tokens=max_tokens,
        )

    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            "Supported: auto, openai, gemini, anthropic, ollama, cohere, mistral"
        )


__all__ = ["create_llm_provider"]

