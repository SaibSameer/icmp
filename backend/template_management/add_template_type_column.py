#!/usr/bin/env python
"""
Template Management Module: Database Schema Migration

This script adds a template_type column to the prompt_templates table if it doesn't exist.
It is part of the template management system and handles database schema migrations
related to template types.

Location: backend/template_management/add_template_type_column.py
"""

import os
import logging
import sys

# Ensure the backend directory is in the path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.db import get_db_connection, release_db_connection

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_template_type_column():
    """Add template_type column to prompt_templates table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prompt_templates' AND column_name = 'template_type'
        """)
        
        if cursor.fetchone():
            logger.info("Column 'template_type' already exists in prompt_templates table")
            return True
        
        # Add the column
        cursor.execute("""
            ALTER TABLE prompt_templates 
            ADD COLUMN template_type VARCHAR(50) DEFAULT 'stage_selection'
        """)
        
        # Update existing templates to have a default type
        cursor.execute("""
            UPDATE prompt_templates
            SET template_type = 'stage_selection'
            WHERE template_type IS NULL
        """)
        
        conn.commit()
        logger.info("Successfully added 'template_type' column to prompt_templates table")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding template_type column: {str(e)}", exc_info=True)
        return False
    finally:
        release_db_connection(conn)

if __name__ == "__main__":
    logger.info("Starting database migration to add template_type column")
    success = add_template_type_column()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        sys.exit(1)