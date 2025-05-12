"""
Database connection utilities.

This module provides utility functions for managing database connections,
including getting and releasing connections from the pool.
"""

import logging
import psycopg2
import psycopg2.pool
from psycopg2.extras import DictCursor
from backend.config import get_db_config

log = logging.getLogger(__name__)

# Get database configuration
DB_CONFIG = get_db_config()

# Initialize connection pool
CONNECTION_POOL = None

def initialize_connection_pool():
    """
    Initialize the database connection pool.
    
    Returns:
        The initialized connection pool
    """
    global CONNECTION_POOL
    
    if not CONNECTION_POOL:
        try:
            CONNECTION_POOL = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **DB_CONFIG,
                cursor_factory=DictCursor
            )
            log.info("Database connection pool created successfully")
        except Exception as e:
            log.error(f"Error creating connection pool: {e}")
            raise
    
    return CONNECTION_POOL

def get_db_connection():
    """
    Get a database connection from the pool.
    
    Returns:
        A database connection object
        
    Raises:
        Exception if no connection can be established
    """
    global CONNECTION_POOL
    
    if not CONNECTION_POOL:
        initialize_connection_pool()
    
    try:
        conn = CONNECTION_POOL.getconn()
        if conn:
            return conn
        raise Exception("Failed to get database connection from pool")
    except Exception as e:
        log.error(f"Error getting database connection: {e}")
        raise

def release_db_connection(conn):
    """
    Release a database connection back to the pool.
    
    Args:
        conn: The database connection to release
    """
    if conn and CONNECTION_POOL:
        try:
            if conn.status != psycopg2.extensions.STATUS_READY:
                conn.rollback()
            CONNECTION_POOL.putconn(conn)
        except Exception as e:
            log.error(f"Error releasing database connection: {e}")
            try:
                conn.close()
            except:
                pass

def execute_query(conn, query, params=None):
    """
    Execute a database query.
    
    Args:
        conn: Database connection
        query: SQL query to execute
        params: Optional parameters for the query
        
    Returns:
        Query results as a list of dictionaries
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return None
    finally:
        cursor.close()

def get_db_pool():
    """
    Get the database connection pool.
    
    Returns:
        The database connection pool object
    """
    if not CONNECTION_POOL:
        initialize_connection_pool()
    return CONNECTION_POOL 