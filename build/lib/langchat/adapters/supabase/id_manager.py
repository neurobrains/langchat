"""
ID Manager module for handling sequential IDs with error recovery and conflict prevention.
"""

import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


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
    
    def initialize(self):
        """
        Initialize ID counters from the database.
        Fetches the row count and maximum ID from each table and sets the counter accordingly.
        """
        if self.initialized:
            return
        
        try:
            # Initialize counters for each table
            self._initialize_table("chat_history")
            self._initialize_table("request_metrics")
            self._initialize_table("feedback")
            
            logger.info("ID Manager initialized successfully")
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing ID Manager: {str(e)}")
            # Set default values if initialization fails
            self.table_counters["chat_history"] = self.initial_value
            self.table_counters["request_metrics"] = self.initial_value
            self.table_counters["feedback"] = self.initial_value
    
    def _initialize_table(self, table_name: str):
        """
        Initialize counter for a specific table by finding both the row count and maximum ID.
        """
        try:
            # First get the total count of rows in the table
            count_response = self.supabase_client.table(table_name) \
                .select("*", count="exact") \
                .execute()
            
            row_count = count_response.count if hasattr(count_response, 'count') else 0
            
            # Then get the maximum ID in the table
            max_id_response = self.supabase_client.table(table_name) \
                .select("id") \
                .order("id", desc=True) \
                .limit(1) \
                .execute()
            
            # Set counter to max(row_count + 1, max_id + 1, initial_value)
            if max_id_response.data and len(max_id_response.data) > 0:
                max_id = max_id_response.data[0]['id']
                next_id = max(row_count + 1, max_id + 1, self.initial_value)
                self.table_counters[table_name] = next_id
                logger.info(f"Initialized {table_name} counter to {self.table_counters[table_name]} (rows: {row_count}, max_id: {max_id})")
            else:
                self.table_counters[table_name] = max(self.initial_value, row_count + 1)
                logger.info(f"No records found in {table_name}, starting counter at {self.table_counters[table_name]}")
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
        last_error = None
        
        while attempts < self.retry_attempts:
            try:
                # Generate a new ID for this attempt
                current_id = self.next_id(table_name)
                
                # Add ID to the data
                insert_data = {"id": current_id, **data}
                
                # Attempt to insert
                response = self.supabase_client.table(table_name) \
                    .insert(insert_data) \
                    .execute()
                
                # If successful, return the response
                return response.data
                
            except Exception as e:
                attempts += 1
                last_error = e
                
                # Check if it's a duplicate key error
                error_str = str(e).lower()
                if "duplicate key" in error_str or "unique constraint" in error_str:
                    logger.warning(f"ID conflict detected for {table_name} with ID {current_id}, retrying...")
                    
                    # Force refresh the counter from the database
                    self._initialize_table(table_name)
                    
                    # Add a small delay before retry
                    time.sleep(0.2)
                else:
                    logger.error(f"Non-duplicate error inserting into {table_name}: {str(e)}")
                
                if attempts >= self.retry_attempts:
                    logger.error(f"Failed to insert into {table_name} after {self.retry_attempts} attempts")
                    return None
        
        return None
