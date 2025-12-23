# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from langchat import LangChatConfig


def test_import_config():
    """Test that LangChatConfig can be imported and instantiated."""

    config = LangChatConfig(openai_api_keys=["test-key"], openai_model="gpt-4o-mini")

    assert config.openai_api_keys == ["test-key"]
    assert config.openai_model == "gpt-4o-mini"
    assert config.timezone == "Asia/Dhaka"


def test_config_get_formatted_time():
    """Test that config can get formatted time."""
    config = LangChatConfig(openai_api_keys=["test-key"], timezone="UTC")

    time_str = config.get_formatted_time()
    assert isinstance(time_str, str)
    assert len(time_str) > 0


def test_dependencies_import():
    """Test that all required dependencies can be imported."""
    import fastapi
    import langchain
    import openai
    import pydantic
    import requests
    import starlette
    import uvicorn

    assert fastapi is not None
    assert uvicorn is not None
    assert starlette is not None
    assert pydantic is not None
    assert requests is not None
    assert langchain is not None
    assert openai is not None
