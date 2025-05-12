#!/usr/bin/env python3
"""
Setup script for managing the test environment in PostgreSQL.
This script creates a test schema to isolate test data from production data.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'name': os.environ.get('DB_NAME', 'icmp_db'),
    'user': os.environ.get('DB_USER', 'icmp_user'),
    'password': os.environ.get('DB_PASSWORD', 'your_password'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}

def connect_to_db():
    """Connect to the database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['name'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        log.error(f"Error connecting to database: {str(e)}")
        raise

def setup_test_schema():
    """Set up the test schema and tables."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Create test schema if it doesn't exist
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS test;
        """)
        log.info("Test schema created or already exists.")
        
        # Get the path to the test migrations directory
        migrations_dir = Path(__file__).parent / 'migrations'
        
        # Execute all migration files in order
        for migration_file in sorted(migrations_dir.glob('*.sql')):
            log.info(f"Executing migration: {migration_file.name}")
            with open(migration_file, 'r') as f:
                sql_script = f.read()
                cursor.execute(sql_script)
        
        log.info("Test schema setup completed successfully.")
        
    except Exception as e:
        log.error(f"Error setting up test schema: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def cleanup_test_schema():
    """Clean up the test schema."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Drop test schema and all its objects
        cursor.execute("""
            DROP SCHEMA IF EXISTS test CASCADE;
        """)
        log.info("Test schema cleaned up successfully.")
        
    except Exception as e:
        log.error(f"Error cleaning up test schema: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    log.info("Starting test environment setup...")
    try:
        setup_test_schema()
        log.info("Test environment setup completed successfully.")
    except Exception as e:
        log.error(f"Test environment setup failed: {str(e)}")
        sys.exit(1) 