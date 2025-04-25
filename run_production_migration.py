#!/usr/bin/env python3
"""
Script to run database migrations on the production database.
"""

import os
import sys
import psycopg2
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add updated_at column to stages table."""
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration from environment variables
    db_config = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT", "5432")
    }
    
    # Ensure all required environment variables are set
    required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        log.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        # Connect to the database
        log.info("Connecting to database...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute the migration script
        log.info("Reading migration script...")
        with open('backend/migrations/04_add_updated_at_to_stages.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            
        log.info("Executing migration script...")
        cursor.execute(sql_script)
        
        log.info("Migration completed successfully!")
        
    except Exception as e:
        log.error(f"An error occurred during migration: {str(e)}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    run_migration() 