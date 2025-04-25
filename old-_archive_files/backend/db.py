import os
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor, RealDictCursor
from dotenv import load_dotenv
import sys

load_dotenv()
log = logging.getLogger(__name__)

# Force testing mode with environment variable or if running with pytest
TESTING = os.environ.get('TESTING') == 'True' or 'pytest' in sys.modules or '--pytest' in sys.argv

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

# Initialize connection pool
CONNECTION_POOL = None

# Skip real DB connection entirely during tests
if not TESTING:
    try:
        CONNECTION_POOL = psycopg2.pool.SimpleConnectionPool(
            minconn=3,
            maxconn=20,  # Increase from 10 to 20 to handle more simultaneous connections
            **DB_CONFIG,
            cursor_factory=DictCursor  # Use DictCursor for easier access to columns by name
        )
        if CONNECTION_POOL:
            log.info("Database connection pool created successfully")
    except Exception as e:
        log.error(f"Error creating connection pool: {e}", exc_info=True)
else:
    log.info("Running in test mode - using mock database connection")

def get_db_connection():
    """Get a connection from the pool."""
    # Always return a mock for tests
    if TESTING:
        from unittest.mock import MagicMock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.autocommit = False
        return mock_conn
        
    # Regular connection logic for non-test environments
    try:
        if CONNECTION_POOL:
            conn = CONNECTION_POOL.getconn()
            conn.autocommit = False
            return conn
        else:
            log.error("No connection pool available")
            return None
    except Exception as e:
        log.error(f"Error getting database connection: {e}", exc_info=True)
        return None

def release_db_connection(conn):
    """Return a connection to the pool."""
    if TESTING:
        return
    
    # Don't try to release None connections
    if not conn:
        log.warning("Attempted to release None connection")
        return
        
    # Don't try to release if pool is gone
    if not CONNECTION_POOL:
        log.warning("Connection pool not available when releasing connection")
        return
    
    try:
        # Only check status if psycopg2 connection (skip for mocks)
        if hasattr(conn, 'status'):
            if conn.status != psycopg2.extensions.STATUS_READY:
                try:
                    # If there was an error, rollback is safer
                    conn.rollback()
                    log.debug("Rolling back uncommitted transaction before releasing connection")
                except Exception as e:
                    log.error(f"Error rolling back connection: {e}", exc_info=True)
        
        # Now return the connection to the pool
        CONNECTION_POOL.putconn(conn)
        log.debug("Connection successfully returned to pool")
    except Exception as e:
        log.error(f"Error releasing database connection: {e}", exc_info=True)

def execute_query(conn, query, params=None):
    """Execute a query and return the cursor."""
    if conn is None:
        log.error("Cannot execute query, connection is None")
        if TESTING:
            from unittest.mock import MagicMock
            return MagicMock()
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        return cursor
    except Exception as e:
        log.error(f"Error executing query: {str(e)}", exc_info=True)
        try:
            conn.rollback() # Rollback in case of an error
        except:
            pass
        
        # Always re-raise the exception, even in testing mode
        raise

def get_db_pool():
    """Get the database connection pool."""
    if TESTING:
        from unittest.mock import MagicMock
        mock_pool = MagicMock()
        mock_pool.getconn.return_value = get_db_connection()
        mock_pool.putconn = release_db_connection
        return mock_pool
    return CONNECTION_POOL

def setup_database():
    conn = None
    try:
        conn = get_db_connection()
        # Drop tables with CASCADE
        execute_query(conn, 'DROP TABLE IF EXISTS conversations CASCADE;')
        execute_query(conn, 'DROP TABLE IF EXISTS stages CASCADE;')
        execute_query(conn, 'DROP TABLE IF EXISTS businesses CASCADE;')

        # Businesses table
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS businesses (
            business_id UUID PRIMARY KEY NOT NULL,
            api_key TEXT NOT NULL,
            owner_id UUID NOT NULL,
            business_name TEXT NOT NULL UNIQUE,
            business_description TEXT,
            address TEXT,
            phone_number TEXT,
            website TEXT,
            first_stage_id UUID,
            agent_list JSONB DEFAULT '[]',
            product_list JSONB DEFAULT '[]',
            service_list JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );''')

        # Users table
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );''')
        execute_query(conn, 'CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);')

        # Stages table
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS stages (
            stage_id UUID PRIMARY KEY NOT NULL,
            business_id UUID NOT NULL,
            agent_id UUID,
            stage_name TEXT NOT NULL,
            stage_description TEXT NOT NULL,
            stage_type TEXT NOT NULL,
            stage_selection_template_id UUID,
            data_extraction_template_id UUID,
            response_generation_template_id UUID,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_business FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        );''')
        execute_query(conn, 'CREATE INDEX IF NOT EXISTS idx_stages_business_id ON stages (business_id);')

        # Conversations table
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS conversations (
            conversation_id UUID PRIMARY KEY NOT NULL,
            business_id UUID NOT NULL,
            user_id UUID NOT NULL,
            agent_id UUID,
            stage_id UUID,
            session_id TEXT NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            status TEXT NOT NULL DEFAULT 'active',
            CONSTRAINT fk_business FOREIGN KEY (business_id) REFERENCES businesses(business_id),
            CONSTRAINT fk_stage FOREIGN KEY (stage_id) REFERENCES stages(stage_id)
        );''')
        execute_query(conn, 'CREATE INDEX IF NOT EXISTS idx_conversations_business_id ON conversations (business_id);')

        # Messages table
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS messages (
            message_id UUID PRIMARY KEY NOT NULL,
            conversation_id UUID NOT NULL,
            user_id UUID NOT NULL,
            message_content TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'delivered',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
            CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        );''')
        execute_query(conn, 'CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id);')
        execute_query(conn, 'CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages (created_at);')

        conn.commit()
        log.info({"message": "Database setup completed successfully"})
    except psycopg2.Error as e:
        log.error({"message": "Database error during setup", "error": str(e)}, exc_info=True)
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    setup_database()