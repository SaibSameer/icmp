#!/usr/bin/env python3

"""
Database Migration Utility

This script runs SQL migration files against the ICMP Events API database.
It can be used to apply structural changes to the database like adding tables,
modifying columns, or migrating data between tables.

Usage:
    python run_migration.py --file <path_to_migration_file>
    python run_migration.py --dir <directory_containing_migrations>
"""

import argparse
import os
import logging
import sys
import psycopg2
from psycopg2 import sql
import re
from typing import List, Optional
import configparser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('db_migration')

def get_connection_details():
    """
    Get database connection details from config file or environment variables.
    """
    # First try to read from config file
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'config', 
        'database.ini'
    )
    
    db_config = {}
    
    # Try to read from config file first
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'database' in config:
            db_section = config['database']
            db_config = {
                'host': db_section.get('host', 'localhost'),
                'dbname': db_section.get('dbname', 'icmp_db'),
                'user': db_section.get('user', 'icmp_user'),
                'password': db_section.get('password', ''),
                'port': db_section.get('port', '5432')
            }
    
    # Override with environment variables if they exist
    db_config['host'] = os.environ.get('DB_HOST', db_config.get('host', 'localhost'))
    db_config['dbname'] = os.environ.get('DB_NAME', db_config.get('dbname', 'icmp_db'))
    db_config['user'] = os.environ.get('DB_USER', db_config.get('user', 'icmp_user'))
    db_config['password'] = os.environ.get('DB_PASSWORD', db_config.get('password', ''))
    db_config['port'] = os.environ.get('DB_PORT', db_config.get('port', '5432'))
    
    return db_config

def connect_to_db(db_config):
    """
    Establish a connection to the database.
    """
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port']
        )
        return conn
    except Exception as e:
        log.error(f"Failed to connect to database: {str(e)}")
        raise

def run_migration_file(file_path: str, conn) -> bool:
    """
    Run a single migration file against the database.
    
    Args:
        file_path: Path to the migration SQL file
        conn: Database connection
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        log.error(f"Migration file not found: {file_path}")
        return False
    
    log.info(f"Running migration: {os.path.basename(file_path)}")
    
    try:
        # Read the SQL file
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Create a cursor
        cursor = conn.cursor()
        
        try:
            # Execute the SQL
            cursor.execute(sql_content)
            conn.commit()
            log.info(f"Migration successful: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            conn.rollback()
            log.error(f"Migration failed: {str(e)}")
            return False
        finally:
            cursor.close()
    except Exception as e:
        log.error(f"Error reading or executing migration file: {str(e)}")
        return False

def run_migrations_in_directory(directory: str, conn) -> List[str]:
    """
    Run all SQL migration files in a directory in numeric order.
    
    Args:
        directory: Directory containing migration files
        conn: Database connection
        
    Returns:
        List[str]: List of failed migrations
    """
    if not os.path.exists(directory):
        log.error(f"Migration directory not found: {directory}")
        return ["Directory not found"]
    
    # Get all SQL files in the directory
    sql_files = [f for f in os.listdir(directory) if f.endswith('.sql')]
    
    # Sort files numerically
    sql_files.sort(key=lambda f: int(re.match(r'^(\d+)', f).group(1)) if re.match(r'^(\d+)', f) else float('inf'))
    
    failed_migrations = []
    
    for sql_file in sql_files:
        file_path = os.path.join(directory, sql_file)
        success = run_migration_file(file_path, conn)
        if not success:
            failed_migrations.append(sql_file)
    
    return failed_migrations

def main():
    """
    Main function to parse arguments and run migrations.
    """
    parser = argparse.ArgumentParser(description='Run database migrations for ICMP Events API')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='Path to a single migration SQL file')
    group.add_argument('--dir', help='Path to directory containing migration SQL files')
    
    args = parser.parse_args()
    
    try:
        # Get database connection details
        db_config = get_connection_details()
        
        # Connect to database
        conn = connect_to_db(db_config)
        
        try:
            # Run migrations
            if args.file:
                success = run_migration_file(args.file, conn)
                sys.exit(0 if success else 1)
            elif args.dir:
                failed_migrations = run_migrations_in_directory(args.dir, conn)
                if failed_migrations:
                    log.error(f"Failed migrations: {', '.join(failed_migrations)}")
                    sys.exit(1)
                else:
                    log.info("All migrations completed successfully")
                    sys.exit(0)
        finally:
            conn.close()
    except Exception as e:
        log.error(f"Migration process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()