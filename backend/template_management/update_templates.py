#!/usr/bin/env python
"""
Template Management Module: Default Template Initialization

This module is responsible for creating and managing default templates in the system.
It ensures that all necessary default templates exist for stage selection,
data extraction, and response generation.

Location: backend/template_management/update_templates.py
"""

from backend.db import get_db_connection, release_db_connection
import logging
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def main():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, find if default templates exist
        cursor.execute("""
            SELECT template_type, COUNT(*) 
            FROM templates 
            WHERE template_type IN ('default_stage_selection', 'default_data_extraction', 'default_response_generation')
            GROUP BY template_type
        """)
        
        existing_types = {row[0]: row[1] for row in cursor.fetchall()}
        log.info(f"Found existing default templates: {existing_types}")
        
        # Check for business ID - we need it to create templates
        cursor.execute("SELECT business_id FROM businesses LIMIT 1")
        business_row = cursor.fetchone()
        
        if not business_row:
            log.error("No business found in database. Can't create default templates.")
            return
            
        business_id = business_row[0]
        log.info(f"Using business ID: {business_id}")
        
        # Create missing default templates
        if 'default_stage_selection' not in existing_types:
            selection_template_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (selection_template_id, business_id, "Default Selection Template", "default_stage_selection", 
                  "Process this message: {{message_content}}", "You are a helpful assistant."))
            log.info(f"Created missing default_stage_selection template: {selection_template_id}")
        
        if 'default_data_extraction' not in existing_types:
            extraction_template_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (extraction_template_id, business_id, "Default Extraction Template", "default_data_extraction",
                  "Extract key information from: {{message_content}}", "Extract relevant information."))
            log.info(f"Created missing default_data_extraction template: {extraction_template_id}")
        
        if 'default_response_generation' not in existing_types:
            response_template_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (response_template_id, business_id, "Default Response Template", "default_response_generation",
                  "Generate a response to: {{message_content}}", "Generate a helpful response."))
            log.info(f"Created missing default_response_generation template: {response_template_id}")
        
        # Get all templates again to verify
        cursor.execute("""
            SELECT template_id, template_name, template_type 
            FROM templates 
            WHERE template_type LIKE 'default_%'
        """)
        
        templates = cursor.fetchall()
        
        print('Default templates:')
        for template in templates:
            print(f'{template[0]}: {template[1]} - {template[2]}')
        
        conn.commit()
        log.info(f"Verified {len(templates)} default templates are in the database")
        
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error updating templates: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    main()