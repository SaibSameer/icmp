#!/usr/bin/env python
# backend/update_template_types.py
"""
Script to update template types in the database.
This will add the 'default_' prefix to templates that should have it.
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db import get_db_connection, release_db_connection

def update_template_types():
    """Update template types to include the 'default_' prefix for default templates."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find templates to update
        cursor.execute("""
            SELECT template_id, template_name, template_type
            FROM templates
            WHERE template_name LIKE 'Default%'
              AND NOT template_type LIKE 'default_%'
        """)
        
        templates_to_update = cursor.fetchall()
        if not templates_to_update:
            log.info("No templates found that need updating.")
            return

        log.info(f"Found {len(templates_to_update)} templates to update.")
        
        # Update each template
        for template_id, template_name, template_type in templates_to_update:
            new_type = f"default_{template_type}"
            
            cursor.execute("""
                UPDATE templates
                SET template_type = %s
                WHERE template_id = %s
            """, (new_type, template_id))
            
            log.info(f"Updated template '{template_name}' (ID: {template_id}): {template_type} -> {new_type}")
        
        conn.commit()
        log.info("Successfully updated all template types.")
        
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error updating template types: {str(e)}")
        raise
    finally:
        if conn:
            release_db_connection(conn)

def main():
    """Run the script."""
    try:
        update_template_types()
        log.info("Script completed successfully.")
    except Exception as e:
        log.error(f"Script failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()