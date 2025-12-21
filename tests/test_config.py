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
if spec is None:
    raise ImportError(f"Could not load spec from {config_module_path}")

config_module = importlib.util.module_from_spec(spec)
if spec.loader is None:
    raise ImportError(f"Spec loader is None for {config_module_path}")

spec.loader.exec_module(config_module)
LangChatConfig = config_module.LangChatConfig


def test_config_default_values():
    """Test that config has correct default values."""
    config = LangChatConfig(openai_api_keys=["test-key"])

    assert config.openai_model == "gpt-4o-mini"
    assert config.openai_temperature == 1.0
    assert config.openai_embedding_model == "text-embedding-3-large"
    assert config.retrieval_k == 5
    assert config.reranker_top_n == 3
    assert config.max_chat_history == 20
    assert config.memory_window == 20
    assert config.timezone == "Asia/Dhaka"
    assert config.server_port == 8000


def test_config_from_env_single_key(monkeypatch):
    """Test creating config from environment variables with single key."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-single-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")

    config = LangChatConfig.from_env()

    assert config.openai_api_keys == ["test-single-key"]
    assert config.openai_model == "gpt-4o"
    assert config.openai_temperature == 0.5


def test_config_from_env_multiple_keys(monkeypatch):
    """Test creating config from environment variables with multiple keys."""
    monkeypatch.setenv("OPENAI_API_KEYS", "key1,key2,key3")

    config = LangChatConfig.from_env()

    assert len(config.openai_api_keys) == 3
    assert "key1" in config.openai_api_keys
    assert "key2" in config.openai_api_keys
    assert "key3" in config.openai_api_keys


def test_config_custom_values():
    """Test that config accepts custom values."""
    config = LangChatConfig(
        openai_api_keys=["test-key"],
        openai_model="gpt-4",
        openai_temperature=0.7,
        retrieval_k=10,
        reranker_top_n=5,
        max_chat_history=30,
        timezone="America/New_York",
    )

    assert config.openai_model == "gpt-4"
    assert config.openai_temperature == 0.7
    assert config.retrieval_k == 10
    assert config.reranker_top_n == 5
    assert config.max_chat_history == 30
    assert config.timezone == "America/New_York"
