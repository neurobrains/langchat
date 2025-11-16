"""
Supabase adapter for database operations.
"""

from typing import Optional

import requests
from supabase import Client, create_client

from langchat.logger import logger


class SupabaseAdapter:
    """
    Adapter for Supabase database operations.
    """

    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL
            key: Supabase API key
        """
        self.url = url
        self.key = key
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """
        Get or create Supabase client.
        """
        if self._client is None:
            self._client = create_client(self.url, self.key)
        return self._client

    @classmethod
    def from_config(cls, supabase_url: str, supabase_key: str) -> "SupabaseAdapter":
        """
        Create adapter from configuration.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key

        Returns:
            SupabaseAdapter instance
        """
        return cls(url=supabase_url, key=supabase_key)

    def create_tables_if_not_exist(self):
        """
        Create required database tables if they don't exist.
        Tries multiple methods to create tables automatically.

        This method will create:
        - chat_history table
        - request_metrics table

        Returns:
            bool: True if tables were created or already exist, False on error
        """
        try:
            # First, check if tables already exist
            try:
                self.client.table("chat_history").select("id").limit(1).execute()
                self.client.table("request_metrics").select("id").limit(1).execute()
                logger.info("Database tables already exist")
                return True
            except Exception as e:
                # Check if it's a "table not found" error
                error_str = str(e).lower()
                if "pgrst205" in error_str or "could not find the table" in error_str:
                    logger.info("Tables not found, attempting to create them...")
                else:
                    # Some other error, might be permissions or connection issue
                    logger.warning(f"Error checking tables (might be permissions): {str(e)}")
                    return False

            # Get SQL to create tables
            create_tables_sql = self.get_create_tables_sql()

            # Try Method 1: Use Supabase Management API (requires service role key)
            if self._create_tables_via_management_api(create_tables_sql):
                logger.info("Tables created successfully via Management API")
                return True

            # Try Method 2: Use custom RPC function (if available)
            if self._create_tables_via_rpc(create_tables_sql):
                logger.info("Tables created successfully via RPC")
                return True

            # Method 3: Provide SQL for manual execution
            logger.warning(
                "\n" + "=" * 80 + "\n"
                "Could not create tables automatically.\n"
                "Please run the following SQL in your Supabase SQL Editor:\n"
                "(Go to: Supabase Dashboard > SQL Editor > New Query)\n"
                "=" * 80 + "\n"
                f"{create_tables_sql}\n"
                "=" * 80 + "\n"
                "After running the SQL, the tables will be created automatically.\n"
                "Alternatively, use a service role key for automatic table creation.\n"
            )
            return False

        except Exception as e:
            logger.error(f"Error in create_tables_if_not_exist: {str(e)}")
            return False

    def _create_tables_via_management_api(self, sql: str) -> bool:
        """
        Try to create tables using Supabase Management API or direct SQL execution.
        This requires a service role key.

        Args:
            sql: SQL statements to execute

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract project reference from URL
            # Format: https://xxxxx.supabase.co -> xxxxx
            project_ref = self.url.replace("https://", "").replace(".supabase.co", "").split("/")[0]

            headers = {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            }

            # Try Method 1: Supabase Management API (if available)
            try:
                management_url = (
                    f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
                )
                response = requests.post(
                    management_url, headers=headers, json={"query": sql}, timeout=30
                )

                if response.status_code in [200, 201, 204]:
                    logger.info("Tables created via Management API")
                    return True
            except Exception:
                pass  # Management API might not be available

            # Try Method 2: Use Supabase REST API with postgrest
            # Try to execute SQL via the REST API's query endpoint
            # This is a workaround and may not work with all setups
            try:
                # Split SQL into individual statements
                statements = [
                    s.strip()
                    for s in sql.split(";")
                    if s.strip() and not s.strip().startswith("--")
                ]

                for statement in statements:
                    if not statement:
                        continue
                    # Try to execute via REST API (this likely won't work, but worth trying)
                    # Note: Supabase REST API doesn't support arbitrary SQL
                    pass
            except Exception:
                pass

            return False

        except Exception as e:
            logger.debug(f"Management API method failed: {str(e)}")
            return False

    def _create_tables_via_rpc(self, sql: str) -> bool:
        """
        Try to create tables using a custom RPC function.
        This requires a pre-created RPC function in Supabase.

        Args:
            sql: SQL statements to execute

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to call a custom RPC function that executes SQL
            # This requires the function to be created in Supabase first
            response = self.client.rpc("exec_sql", {"query": sql}).execute()

            if response.data:
                logger.info("Tables created via RPC function")
                return True
            else:
                return False

        except Exception as e:
            # RPC function might not exist, which is expected
            logger.debug(f"RPC method failed (function may not exist): {str(e)}")
            return False

    def get_create_tables_sql(self) -> str:
        """
        Get the SQL statements needed to create required tables.
        Useful for manual execution or documentation.

        Returns:
            str: SQL statements to create tables
        """
        return """
-- Create chat_history table
CREATE TABLE IF NOT EXISTS public.chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL DEFAULT 'default',
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for chat_history
CREATE INDEX IF NOT EXISTS idx_chat_history_user_domain
    ON public.chat_history(user_id, domain);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp
    ON public.chat_history(timestamp DESC);

-- Create request_metrics table
CREATE TABLE IF NOT EXISTS public.request_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    request_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time DOUBLE PRECISION NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- Create indexes for request_metrics
CREATE INDEX IF NOT EXISTS idx_request_metrics_user_id
    ON public.request_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_request_metrics_request_time
    ON public.request_metrics(request_time DESC);

-- Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';
"""
