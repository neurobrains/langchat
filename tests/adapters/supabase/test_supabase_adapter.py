"""
Tests for SupabaseAdapter.
"""

from unittest.mock import MagicMock, patch

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

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_get_create_tables_sql(self, mock_create_client):
        """Test get_create_tables_sql method."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        sql = adapter.get_create_tables_sql()

        assert isinstance(sql, str)
        assert "CREATE TABLE IF NOT EXISTS public.chat_history" in sql
        assert "CREATE TABLE IF NOT EXISTS public.request_metrics" in sql
        assert "NOTIFY pgrst, 'reload schema'" in sql

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_create_tables_if_not_exist_tables_exist(self, mock_create_client):
        """Test create_tables_if_not_exist when tables already exist."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        mock_create_client.return_value = mock_client

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        result = adapter.create_tables_if_not_exist()

        assert result is True
        assert mock_client.table.call_count == 2

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    @patch("langchat.adapters.supabase.supabase_adapter.requests.post")
    def test_create_tables_if_not_exist_via_management_api(self, mock_post, mock_create_client):
        """Test create_tables_if_not_exist using Management API."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table

        # First call raises error (table doesn't exist)
        # Second call also raises error
        def side_effect(*args, **kwargs):
            raise Exception("PGRST205: Could not find the table")

        mock_table.execute.side_effect = side_effect
        mock_create_client.return_value = mock_client

        # Mock successful Management API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        result = adapter.create_tables_if_not_exist()

        assert result is True
        assert mock_post.called

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_create_tables_if_not_exist_via_rpc(self, mock_create_client):
        """Test create_tables_if_not_exist using RPC function."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table

        # First call raises error (table doesn't exist)
        def side_effect(*args, **kwargs):
            raise Exception("PGRST205: Could not find the table")

        mock_table.execute.side_effect = side_effect

        # Mock RPC call
        mock_rpc = MagicMock()
        mock_rpc.execute.return_value = MagicMock(data=True)
        mock_client.rpc.return_value = mock_rpc
        mock_create_client.return_value = mock_client

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        result = adapter.create_tables_if_not_exist()

        assert result is True
        assert mock_client.rpc.called

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    @patch("langchat.adapters.supabase.supabase_adapter.requests.post")
    def test_create_tables_if_not_exist_fallback_to_sql(self, mock_post, mock_create_client):
        """Test create_tables_if_not_exist falls back to providing SQL."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table

        # First call raises error (table doesn't exist)
        def side_effect(*args, **kwargs):
            raise Exception("PGRST205: Could not find the table")

        mock_table.execute.side_effect = side_effect
        mock_create_client.return_value = mock_client

        # Mock failed Management API response
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_post.return_value = mock_response

        # Mock failed RPC call
        def rpc_side_effect(*args, **kwargs):
            raise Exception("Function does not exist")

        mock_client.rpc.side_effect = rpc_side_effect

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        result = adapter.create_tables_if_not_exist()

        assert result is False

    @patch("langchat.adapters.supabase.supabase_adapter.create_client")
    def test_create_tables_if_not_exist_other_error(self, mock_create_client):
        """Test create_tables_if_not_exist with non-table error."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table

        # Raise a different error (not table not found)
        def side_effect(*args, **kwargs):
            raise Exception("Connection error")

        mock_table.execute.side_effect = side_effect
        mock_create_client.return_value = mock_client

        adapter = SupabaseAdapter(
            url="https://test.supabase.co",
            key="test-key",
        )

        result = adapter.create_tables_if_not_exist()

        assert result is False
