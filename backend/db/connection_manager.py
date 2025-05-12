"""
Connection manager for handling database connections with retry logic.

This module provides a robust way to manage database connections,
including automatic retries and proper error handling.
"""

import logging
import time
from typing import Optional, Callable, Any
import psycopg2
from psycopg2.extensions import connection
from contextlib import contextmanager

log = logging.getLogger(__name__)

class ConnectionManager:
    """Manages database connections with retry logic and error handling."""
    
    def __init__(self, db_pool, max_retries: int = 3, retry_delay: float = 0.5):
        """
        Initialize the connection manager.
        
        Args:
            db_pool: Database connection pool
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.db_pool = db_pool
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        log.info(f"ConnectionManager initialized with max_retries={max_retries}, retry_delay={retry_delay}")
    
    @contextmanager
    def get_connection(self) -> connection:
        """
        Get a database connection with retry logic.
        
        Yields:
            A database connection
            
        Raises:
            Exception if all retry attempts fail
        """
        conn = None
        last_error = None
        
        try:
            for attempt in range(self.max_retries):
                try:
                    log.info(f"Attempting to get connection (attempt {attempt + 1}/{self.max_retries})")
                    conn = self.db_pool.getconn()
                    if conn:
                        # Test the connection
                        with conn.cursor() as cur:
                            cur.execute("SELECT 1")
                            if cur.fetchone()[0] == 1:
                                log.info("Successfully obtained and tested database connection")
                                try:
                                    yield conn
                                    return
                                finally:
                                    if conn:
                                        log.info("Releasing connection back to pool")
                                        self.release_connection(conn)
                                        conn = None
                
                except Exception as e:
                    last_error = e
                    log.error(f"Connection attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                    if conn:
                        log.info("Releasing failed connection")
                        self.release_connection(conn)
                        conn = None
                    
                if attempt < self.max_retries - 1:
                    log.info(f"Waiting {self.retry_delay} seconds before next attempt")
                    time.sleep(self.retry_delay)
            
            error_msg = f"Failed to get valid database connection after {self.max_retries} attempts. Last error: {str(last_error)}"
            log.error(error_msg)
            raise Exception(error_msg)
            
        finally:
            if conn:
                log.info("Releasing connection in finally block")
                self.release_connection(conn)
    
    def execute_with_retry(self, func: Callable[[connection], Any]) -> Any:
        """
        Execute a function with a database connection, with retry logic.
        
        Args:
            func: Function to execute with the connection
            
        Returns:
            Result of the function execution
            
        Raises:
            Exception if all retry attempts fail
        """
        log.info("Executing function with retry logic")
        with self.get_connection() as conn:
            try:
                result = func(conn)
                log.info("Function executed successfully")
                return result
            except Exception as e:
                log.error(f"Error executing function: {str(e)}", exc_info=True)
                raise
    
    def release_connection(self, conn: connection) -> None:
        """
        Safely release a connection back to the pool.
        
        Args:
            conn: Connection to release
        """
        if conn:
            try:
                if conn.status != psycopg2.extensions.STATUS_READY:
                    log.warning("Connection not in READY state, rolling back before release")
                    conn.rollback()
                log.info("Returning connection to pool")
                self.db_pool.putconn(conn)
            except Exception as e:
                log.error(f"Error releasing connection: {str(e)}", exc_info=True)
                try:
                    log.info("Attempting to close connection after release error")
                    conn.close()
                except Exception as close_error:
                    log.error(f"Error closing connection: {str(close_error)}", exc_info=True) 