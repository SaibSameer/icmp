"""
Database utilities for variable providers.

Provides common database operations with proper error handling and connection management.
"""

import logging
import psycopg2
from typing import Dict, Any, List, Optional
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)

class DatabaseUtils:
    """Utility class for database operations."""
    
    @staticmethod
    def get_connection():
        """
        Get a database connection.
        
        Returns:
            Database connection object
            
        Raises:
            Exception if connection fails
        """
        try:
            conn = psycopg2.connect(
                dbname="icmp_db",
                user="icmp_user",
                password="your_password",  # Replace with actual password
                host="localhost",
                port="5432",
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            log.error(f"Failed to connect to database: {str(e)}")
            raise
    
    @staticmethod
    def execute_query(conn, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as dictionaries.
        
        Args:
            conn: Database connection
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            log.error(f"Query execution failed: {str(e)}")
            return []
    
    @staticmethod
    def execute_scalar(conn, query: str, params: tuple = None) -> Optional[Any]:
        """
        Execute a query that returns a single value.
        
        Args:
            conn: Database connection
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Single value result or None
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            log.error(f"Scalar query execution failed: {str(e)}")
            return None
    
    @staticmethod
    def execute_update(conn, query: str, params: tuple = None) -> int:
        """
        Execute an update query and return number of affected rows.
        
        Args:
            conn: Database connection
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            log.error(f"Update query execution failed: {str(e)}")
            conn.rollback()
            return 0 