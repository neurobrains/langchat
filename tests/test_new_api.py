# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for the new LangChat 2.0 API."""

import pytest


def test_version():
    """Test that version is set."""
    import langchat

    assert hasattr(langchat, "__version__")
    assert langchat.__version__ == "1.0.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
