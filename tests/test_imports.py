"""
Test that all imports work correctly.
"""

import importlib.util
from pathlib import Path

# Import config directly to avoid triggering __init__.py imports
config_module_path = Path(__file__).parent.parent / "src" / "langchat" / "config.py"
spec = importlib.util.spec_from_file_location("langchat.config", config_module_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
LangChatConfig = config_module.LangChatConfig


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
