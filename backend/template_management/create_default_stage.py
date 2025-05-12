#!/usr/bin/env python
"""
Template Management Module: Default Stage Creation

This module is responsible for creating default stages and their associated templates.
It ensures that each business has at least one valid stage with proper templates.

Location: backend/template_management/create_default_stage.py
"""

import uuid
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

from backend.db import get_db_connection, release_db_connection

def create_default_stage(business_id=None):
    """Create a default stage for a business if it doesn't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create templates table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                template_id UUID PRIMARY KEY,
                business_id UUID NOT NULL REFERENCES businesses(business_id),
                template_name VARCHAR(255) NOT NULL,
                template_type VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                system_prompt TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        log.info("Ensured templates table exists")
        
        # If no business_id provided, try to find a default business
        if not business_id:
            log.info("No business_id provided, trying to find a default business...")
            cursor.execute("SELECT business_id FROM businesses LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                business_id = result[0]
                log.info(f"Found existing business: {business_id}")
            else:
                log.warning("No businesses found in the database. Creating default business...")
                # Create a default business
                business_id = str(uuid.uuid4())
                owner_id = str(uuid.uuid4())  # Generate a default owner ID
                
                # Get the API key from environment variable
                api_key = os.environ.get('ICMP_API_KEY', 'default_api_key')
                log.info(f"Using API key from environment: {api_key}")
                
                cursor.execute("""
                    INSERT INTO businesses (
                        business_id, business_name, business_description, 
                        created_at, api_key, owner_id
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    business_id,
                    "Default Business",
                    "A default business for testing",
                    datetime.now(),
                    api_key,
                    owner_id
                ))
                conn.commit()
                log.info(f"Created default business: {business_id}")
        
        # Check if a default stage already exists
        cursor.execute("""
            SELECT stage_id FROM stages 
            WHERE business_id = %s AND stage_name = 'Default Conversation Stage'
        """, (business_id,))
        
        if cursor.fetchone():
            log.info("Default stage already exists")
            return None
            
        log.info("Creating default templates...")
        
        # Create default templates
        selection_template_id = str(uuid.uuid4())
        extraction_template_id = str(uuid.uuid4())
        response_template_id = str(uuid.uuid4())
        
        # Insert templates
        cursor.execute("""
            INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (selection_template_id, business_id, "Default Selection Template", "default_stage_selection", 
              "Process this message: {{message_content}}", "You are a helpful assistant."))
        log.info(f"Created stage selection template: {selection_template_id}")
        
        cursor.execute("""
            INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (extraction_template_id, business_id, "Default Extraction Template", "default_data_extraction",
              "Extract key information from: {{message_content}}", "Extract relevant information."))
        log.info(f"Created data extraction template: {extraction_template_id}")
        
        cursor.execute("""
            INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (response_template_id, business_id, "Default Response Template", "default_response_generation",
              "Generate a response to: {{message_content}}", "Generate a helpful response."))
        log.info(f"Created response generation template: {response_template_id}")
        
        # Create the default stage
        stage_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO stages (
                stage_id, business_id, stage_name, stage_description,
                stage_type, stage_selection_template_id, data_extraction_template_id,
                response_generation_template_id, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
        """, (
            stage_id,
            business_id,
            "Default Conversation Stage",
            "Initial stage for new conversations",
            "conversation",
            selection_template_id,
            extraction_template_id,
            response_template_id
        ))
        
        conn.commit()
        log.info(f"Created default stage: {stage_id}")
        return stage_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error creating default stage: {str(e)}")
        raise
    finally:
        if conn:
            release_db_connection(conn)

def main():
    """Run the script."""
    try:
        business_id = None
        if len(sys.argv) > 1:
            business_id = sys.argv[1]
            log.info(f"Using business ID from command line: {business_id}")
        
        result = create_default_stage(business_id)
        log.info(f"Default stage created or found: {result}")
        
    except Exception as e:
        log.error(f"Script failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 