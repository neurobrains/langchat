"""
Tests for SupabaseAdapter.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchat.adapters.supabase.supabase_adapter import SupabaseAdapter


class TestSupabaseAdapter:
    """Test cases for SupabaseAdapter."""

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_adapter_initialization(self, mock_create_client):
        """Test adapter initialization."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )
        
        assert adapter.url == "https://test.supabase.co"
        assert adapter.key == "test-key"

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_adapter_client_property(self, mock_create_client):
        """Test client property."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )
        
        # First access creates client
        client = adapter.client
        assert client is not None
        assert client == mock_client
        
        # Second access uses cached client
        client2 = adapter.client
        assert client2 == client
        
        # Verify create_client was only called once
        assert mock_create_client.call_count == 1

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_adapter_from_config_classmethod(self, mock_create_client):
        """Test from_config classmethod."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        adapter = SupabaseAdapter.from_config(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
        )
        
        assert isinstance(adapter, SupabaseAdapter)
        assert adapter.url == "https://test.supabase.co"
        assert adapter.key == "test-key"

