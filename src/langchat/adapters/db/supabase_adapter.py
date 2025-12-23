# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from typing import Optional

import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from supabase import Client, create_client

from langchat.logger import logger

# Class-level flag to prevent duplicate SQL printing
_sql_printed = False

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

    def get_create_tables_sql(self) -> str:
        """
        Get the SQL statements needed to create required tables with RLS enabled.
        Useful for manual execution or documentation.

        Returns:
            str: SQL statements to create tables with RLS policies
        """
        return """-- LangChat Database Schema with RLS
-- Works with both service_role (recommended) and anon keys
-- Run in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- Note: With anon key, ensure your app validates user_id server-side for security

-- Create tables
CREATE TABLE IF NOT EXISTS public.chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL DEFAULT 'default',
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.request_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    request_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time DOUBLE PRECISION NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_chat_history_user_domain ON public.chat_history(user_id, domain);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON public.chat_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON public.chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_request_metrics_user_id ON public.request_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_request_metrics_request_time ON public.request_metrics(request_time DESC);

-- Enable RLS
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.request_metrics ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Works with service_role (bypasses RLS) and anon key
-- Note: With anon key, app must validate user_id server-side for security

CREATE POLICY "chat_history_policy" ON public.chat_history FOR ALL
    USING (auth.role() = 'service_role' OR user_id IS NOT NULL)
    WITH CHECK (auth.role() = 'service_role' OR user_id IS NOT NULL);

CREATE POLICY "request_metrics_policy" ON public.request_metrics FOR ALL
    USING (auth.role() = 'service_role' OR user_id IS NOT NULL)
    WITH CHECK (auth.role() = 'service_role' OR user_id IS NOT NULL);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
"""

    def check_tables_exist(self):
        """
        Check if the tables exist by attempting to query them.
        Returns True if both tables exist and are accessible, False otherwise.
        """
        try:
            # Try to query both tables - if they exist, this won't throw an error
            # Even if tables are empty, the query should succeed
            self.client.table("chat_history").select("id").limit(1).execute()
            self.client.table("request_metrics").select("id").limit(1).execute()

        except Exception:
            # Create formatted SQL code block
            # Note: lexer is the second positional argument, not a keyword
            if not _sql_printed:
                sql_code = Syntax(
                    self.get_create_tables_sql(),
                    "sql",  # lexer as second positional argument
                    theme="monokai",
                    line_numbers=True,
                )

                # Create info panel
                info_text = (
                    "[bold yellow]⚠ Could not create tables automatically[/bold yellow]\n\n"
                    "[bold]Please run the following SQL in your Supabase SQL Editor:[/bold]\n"
                    "[dim]Go to: Supabase Dashboard > SQL Editor > New Query[/dim]\n\n"
                    "[dim]After running the SQL, the tables will be created automatically.[/dim]\n"
                    "[dim]Alternatively, use a service role key for automatic table creation.[/dim]\n\n"
                    "[bold green]✓ RLS (Row Level Security) is included in the SQL[/bold green]"
                )

                # Print warning message
                logger.warning("Table was not created automatically")

                # Print formatted SQL in a beautiful panel
                console = Console()
                console.print()
                console.print(
                    Panel(
                        info_text,
                        title="[bold yellow]Database Setup Required[/bold yellow]",
                        border_style="yellow",
                    )
                )
                console.print()
                console.print(
                    Panel(
                        sql_code,
                        title="[bold cyan]SQL Schema with RLS[/bold cyan]",
                        border_style="cyan",
                    )
                )
                console.print()

                # Copy SQL to clipboard (with error handling)
                try:
                    pyperclip.copy(self.get_create_tables_sql())
                    logger.info("SQL has been copied to clipboard")
                except Exception:
                    logger.debug("Could not copy to clipboard")
