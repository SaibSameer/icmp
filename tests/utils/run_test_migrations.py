"""
Script to run test database migrations.
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database configuration
TEST_DB_CONFIG = {
    'dbname': os.getenv('TEST_DB_NAME', 'icmp_test'),
    'user': os.getenv('TEST_DB_USER', 'postgres'),
    'password': os.getenv('TEST_DB_PASSWORD', 'postgres'),
    'host': os.getenv('TEST_DB_HOST', 'localhost'),
    'port': os.getenv('TEST_DB_PORT', '5432')
}

def create_test_database():
    """Create the test database if it doesn't exist."""
    # Connect to default database
    conn = psycopg2.connect(
        dbname='postgres',
        user=TEST_DB_CONFIG['user'],
        password=TEST_DB_CONFIG['password'],
        host=TEST_DB_CONFIG['host'],
        port=TEST_DB_CONFIG['port']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    try:
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_CONFIG['dbname'],))
            exists = cursor.fetchone()
            
            if not exists:
                logger.info(f"Creating test database: {TEST_DB_CONFIG['dbname']}")
                cursor.execute(f"CREATE DATABASE {TEST_DB_CONFIG['dbname']}")
                logger.info("Test database created successfully")
            else:
                logger.info(f"Test database {TEST_DB_CONFIG['dbname']} already exists")
    
    finally:
        conn.close()

def run_migrations():
    """Run all test database migrations."""
    # Create test database if it doesn't exist
    create_test_database()
    
    # Connect to test database
    conn = psycopg2.connect(**TEST_DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # Get all migration files
            migrations_dir = Path(__file__).parent.parent / 'migrations'
            migration_files = sorted(migrations_dir.glob('*.sql'))
            
            for migration_file in migration_files:
                logger.info(f"Running migration: {migration_file.name}")
                
                # Read and execute migration file
                with open(migration_file, 'r') as f:
                    migration_sql = f.read()
                    cursor.execute(migration_sql)
                
                logger.info(f"Migration {migration_file.name} completed successfully")
        
        conn.commit()
        logger.info("All migrations completed successfully")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error running migrations: {str(e)}")
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        run_migrations()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1) 