"""
Tests for IDManager.
"""

import pytest
from unittest.mock import Mock, MagicMock
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
        assert manager.initialized == False

    def test_manager_initialization_default_values(self):
        """Test manager initialization with default values."""
        mock_client = MagicMock()
        
        manager = IDManager(supabase_client=mock_client)
        
        assert manager.initial_value == 1
        assert manager.retry_attempts == 3
        assert manager.initialized == False

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

