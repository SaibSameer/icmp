#!/usr/bin/env python
"""
Database Connection Test Module

This module tests the database connection and verifies basic database operations.
It is part of the core utilities for the ICMP API.

Location: backend/utils/connection_test.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.db import get_db_connection, release_db_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def test_connection():
    """Test database connection and basic operations."""
    conn = None
    try:
        log.info("Attempting to connect to database...")
        conn = get_db_connection()
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        log.info(f"Successfully connected to database. Version: {version[0]}")
        
        # Test businesses table
        cursor.execute("SELECT COUNT(*) FROM businesses;")
        count = cursor.fetchone()
        log.info(f"Found {count[0]} businesses in the database")
        
        return True
        
    except Exception as e:
        log.error(f"Database connection test failed: {str(e)}")
        return False
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)