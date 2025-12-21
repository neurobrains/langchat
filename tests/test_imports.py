# Copyright (c) 2025 NeuroBrain Co Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
