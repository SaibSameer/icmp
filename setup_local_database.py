#!/usr/bin/env python3
"""
Setup script for creating the local PostgreSQL database for development.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

def create_database():
    """Create the ICMP database and tables."""
    
    DB_NAME = os.environ.get("DB_NAME", "icmp_db")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    
    # Connect to PostgreSQL to create database
    try:
        # Connect to default postgres database first
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            log.info(f"Database '{DB_NAME}' created successfully.")
        else:
            log.info(f"Database '{DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
        
        # Now connect to the newly created database to create tables
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create tables
        with open('database_setup.sql', 'r') as f:
            sql_script = f.read()
            cursor.execute(sql_script)
        
        log.info("Tables created successfully.")
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        log.error(f"Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    log.info("Starting local database setup...")
    if create_database():
        log.info("Local database setup completed successfully.")
    else:
        log.error("Local database setup failed.")
        sys.exit(1) 