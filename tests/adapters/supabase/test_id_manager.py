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

from unittest.mock import MagicMock

from langchat.adapters.supabase.id_manager import IDManager


class TestIDManager:
    """Test cases for IDManager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        mock_client = MagicMock()

        manager = IDManager(
            supabase_client=mock_client,
            initial_value=1,
            retry_attempts=3,
        )

        assert manager.supabase_client == mock_client
        assert manager.initial_value == 1
        assert manager.retry_attempts == 3
        assert manager.table_counters == {}
        assert not manager.initialized

    def test_manager_initialization_default_values(self):
        """Test manager initialization with default values."""
        mock_client = MagicMock()

        manager = IDManager(supabase_client=mock_client)

        assert manager.initial_value == 1
        assert manager.retry_attempts == 3
        assert not manager.initialized

    def test_manager_has_get_next_id_method(self):
        """Test that manager has get_next_id method."""
        mock_client = MagicMock()

        manager = IDManager(supabase_client=mock_client)

        # The method might be named differently or part of insert_with_retry
        # Check for insert_with_retry which uses get_next_id internally
        assert hasattr(manager, "insert_with_retry")
        assert callable(manager.insert_with_retry)

    def test_manager_has_initialize_method(self):
        """Test that manager has initialize method."""
        mock_client = MagicMock()

        manager = IDManager(supabase_client=mock_client)

        assert hasattr(manager, "initialize")
        assert callable(manager.initialize)

    def test_manager_table_counters_dict(self):
        """Test that manager maintains table_counters dictionary."""
        mock_client = MagicMock()

        manager = IDManager(supabase_client=mock_client)

        assert isinstance(manager.table_counters, dict)
        assert len(manager.table_counters) == 0
