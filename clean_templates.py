#!/usr/bin/env python3
"""
Script to clean up templates that are not registered to any stage.
This script will:
1. Find all templates that are not referenced in any stage's template fields
2. Delete those unused templates
3. Log the cleanup process
"""

import logging
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from db import get_db_connection, release_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

def find_unused_templates(conn):
    """
    Find templates that are not referenced in any stage.
    
    Args:
        conn: Database connection
        
    Returns:
        List of template IDs that are not used by any stage
    """
    cursor = conn.cursor()
    
    # Get all template IDs that are not referenced in any stage
    cursor.execute("""
        SELECT t.template_id, t.template_name, t.template_type
        FROM templates t
        WHERE NOT EXISTS (
            SELECT 1 FROM stages s
            WHERE s.stage_selection_template_id = t.template_id
            OR s.data_extraction_template_id = t.template_id
            OR s.response_generation_template_id = t.template_id
        )
    """)
    
    unused_templates = cursor.fetchall()
    return unused_templates

def delete_unused_templates(conn, unused_templates):
    """
    Delete the unused templates from the database.
    
    Args:
        conn: Database connection
        unused_templates: List of (template_id, template_name, template_type) tuples
    """
    cursor = conn.cursor()
    
    for template_id, template_name, template_type in unused_templates:
        try:
            cursor.execute("DELETE FROM templates WHERE template_id = %s", (template_id,))
            log.info(f"Deleted unused template: {template_name} (ID: {template_id}, Type: {template_type})")
        except Exception as e:
            log.error(f"Error deleting template {template_id}: {str(e)}")
            conn.rollback()
            return False
    
    conn.commit()
    return True

def main():
    """Main function to clean up unused templates."""
    conn = None
    try:
        log.info("Starting template cleanup process...")
        
        # Get database connection
        conn = get_db_connection()
        
        # Find unused templates
        unused_templates = find_unused_templates(conn)
        
        if not unused_templates:
            log.info("No unused templates found. Database is clean.")
            return
        
        # Log found templates
        log.info(f"Found {len(unused_templates)} unused templates:")
        for template_id, template_name, template_type in unused_templates:
            log.info(f"- {template_name} (ID: {template_id}, Type: {template_type})")
        
        # Confirm deletion
        response = input("\nDo you want to delete these unused templates? (yes/no): ")
        if response.lower() != 'yes':
            log.info("Template cleanup cancelled by user.")
            return
        
        # Delete unused templates
        if delete_unused_templates(conn, unused_templates):
            log.info("Successfully cleaned up unused templates.")
        else:
            log.error("Failed to clean up some templates. Check the logs for details.")
            
    except Exception as e:
        log.error(f"Error during template cleanup: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            release_db_connection(conn)
            log.info("Database connection closed.")

if __name__ == "__main__":
    main()