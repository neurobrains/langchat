"""
ID Manager module for handling sequential IDs with error recovery and conflict prevention.
"""

import time
from typing import Any, Dict, Optional

from langchat.logger import logger


class IDManager:
    """
    Manages sequential IDs for database tables with conflict resolution.
    """

    def __init__(self, supabase_client, initial_value: int = 1, retry_attempts: int = 3):
        """
        Initialize ID Manager.

        Args:
            supabase_client: Supabase client instance
            initial_value: Starting ID value
            retry_attempts: Number of retry attempts on conflict
        """
        self.supabase_client = supabase_client
        self.initial_value = initial_value
        self.retry_attempts = retry_attempts
        self.table_counters: Dict[str, int] = {}
        self.initialized = False
        self._initializing = False  # Flag to prevent concurrent initialization

    def initialize(self):
        """
        Initialize ID counters from the database.
        Fetches the row count and maximum ID from each table and sets the counter accordingly.
        """
        # Double-check pattern with flag to prevent concurrent initialization
        if self.initialized:
            return

        # Check if another thread is already initializing
        if self._initializing:
            # Wait a bit and check again
            time.sleep(0.1)
            if self.initialized:
                return

        # Set initializing flag
        self._initializing = True

        try:
            # Double-check again after acquiring lock
            if self.initialized:
                self._initializing = False
                return

            # Initialize counters for each table
            self._initialize_table("chat_history")
            self._initialize_table("request_metrics")

            self.initialized = True
            logger.info("ID Manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ID Manager: {str(e)}")
            # Set default values if initialization fails
            self.table_counters["chat_history"] = self.initial_value
            self.table_counters["request_metrics"] = self.initial_value
            self.initialized = True  # Mark as initialized even on error to prevent retry loops
        finally:
            self._initializing = False

    def _initialize_table(self, table_name: str):
        """
        Initialize counter for a specific table by finding both the row count and maximum ID.
        """
        try:
            # First get the total count of rows in the table
            count_response = (
                self.supabase_client.table(table_name).select("*", count="exact").execute()
            )

            row_count = count_response.count if hasattr(count_response, "count") else 0

            # Then get the maximum ID in the table
            max_id_response = (
                self.supabase_client.table(table_name)
                .select("id")
                .order("id", desc=True)
                .limit(1)
                .execute()
            )

            # Set counter to max(row_count + 1, max_id + 1, initial_value)
            if max_id_response.data and len(max_id_response.data) > 0:
                max_id = max_id_response.data[0]["id"]
                next_id = max(row_count + 1, max_id + 1, self.initial_value)
                self.table_counters[table_name] = next_id
                # Log removed for cleaner output
            else:
                self.table_counters[table_name] = max(self.initial_value, row_count + 1)
                # Log removed for cleaner output
        except Exception as e:
            logger.error(f"Error initializing counter for {table_name}: {str(e)}")
            self.table_counters[table_name] = self.initial_value

    def next_id(self, table_name: str) -> int:
        """
        Get the next available ID for the specified table.
        """
        if not self.initialized:
            self.initialize()

        if table_name not in self.table_counters:
            self.table_counters[table_name] = self.initial_value

        current_id = self.table_counters[table_name]
        self.table_counters[table_name] += 1
        return current_id

    def insert_with_retry(self, table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert data into the specified table with automatic ID generation and retry on conflicts.

        Args:
            table_name: Name of the table to insert into
            data: Dictionary of data to insert (without ID)

        Returns:
            Response data if successful, None if all retries failed
        """
        if not self.initialized:
            self.initialize()

        attempts = 0

        while attempts < self.retry_attempts:
            try:
                # Generate a new ID for this attempt
                current_id = self.next_id(table_name)

                # Add ID to the data
                insert_data = {"id": current_id, **data}

                # Attempt to insert
                response = self.supabase_client.table(table_name).insert(insert_data).execute()

                # If successful, return the response
                return response.data  # type: ignore[no-any-return]

            except Exception as e:
                attempts += 1

                # Check if it's a duplicate key error
                error_str = str(e).lower()
                if "duplicate key" in error_str or "unique constraint" in error_str:
                    logger.warning(
                        f"ID conflict detected for {table_name} with ID {current_id}, retrying..."
                    )

                    # Force refresh the counter from the database
                    self._initialize_table(table_name)

                    # Add a small delay before retry
                    time.sleep(0.2)
                else:
                    logger.error(f"Non-duplicate error inserting into {table_name}: {str(e)}")

                if attempts >= self.retry_attempts:
                    logger.error(
                        f"Failed to insert into {table_name} after {self.retry_attempts} attempts"
                    )
                    return None

        return None
