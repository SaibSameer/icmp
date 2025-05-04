"""
Script to populate monitoring tables with test data.
"""

import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
import json
import uuid
import random
from typing import Dict, Any

# Database configuration
DB_CONFIG = {
    'dbname': 'icmp_db',
    'user': 'icmp_user',
    'password': 'your_password',  # Replace with actual password
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)

def populate_templates(conn):
    """Populate templates table with test data."""
    cursor = conn.cursor()
    
    # Use the existing business_id
    business_id = 'bc7e1824-49b4-4056-aabe-b045a1f79e3b'
    
    # Sample templates
    templates = [
        {
            'template_id': str(uuid.uuid4()),
            'business_id': business_id,
            'template_name': 'Contact Information',
            'template_type': 'data_extraction',
            'content': 'Extract name, email, and phone from the message',
            'system_prompt': 'Extract contact information from the message'
        },
        {
            'template_id': str(uuid.uuid4()),
            'business_id': business_id,
            'template_name': 'Order Details',
            'template_type': 'data_extraction',
            'content': 'Extract order number, product, and quantity',
            'system_prompt': 'Extract order details from the message'
        }
    ]
    
    for template in templates:
        cursor.execute("""
            INSERT INTO templates 
            (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            template['template_id'],
            template['business_id'],
            template['template_name'],
            template['template_type'],
            template['content'],
            template['system_prompt']
        ))
    
    conn.commit()
    return templates

def populate_extraction_results(conn, templates):
    """Populate extraction_results table with test data."""
    cursor = conn.cursor()
    
    # Use the existing business_id
    business_id = 'bc7e1824-49b4-4056-aabe-b045a1f79e3b'
    
    # Generate test data for the last 7 days
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        for template in templates:
            for _ in range(random.randint(5, 15)):  # 5-15 extractions per day per template
                success = random.random() > 0.2  # 80% success rate
                cursor.execute("""
                    INSERT INTO extraction_results 
                    (template_id, business_id, timestamp, success, extracted_data)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    template['template_id'],
                    business_id,
                    date,
                    success,
                    json.dumps({
                        'field1': 'value1',
                        'field2': 'value2'
                    })
                ))
    
    conn.commit()

def populate_processing_stages(conn, templates):
    """Populate processing_stages table with test data."""
    cursor = conn.cursor()
    
    # Use the existing business_id
    business_id = 'bc7e1824-49b4-4056-aabe-b045a1f79e3b'
    
    stages = ['preprocessing', 'extraction', 'validation', 'postprocessing']
    
    # First get some extraction_ids to reference
    cursor.execute("SELECT extraction_id FROM extraction_results LIMIT 10")
    extraction_ids = [row[0] for row in cursor.fetchall()]
    
    if not extraction_ids:
        # If no extraction_results exist yet, create some
        for _ in range(10):
            cursor.execute("""
                INSERT INTO extraction_results 
                (template_id, business_id, timestamp, success, extracted_data)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING extraction_id
            """, (
                templates[0]['template_id'],
                business_id,
                datetime.now(),
                True,
                json.dumps({'test': 'data'})
            ))
            extraction_ids.append(cursor.fetchone()[0])
        conn.commit()
    
    for extraction_id in extraction_ids:
        for stage in stages:
            success = random.random() > 0.1  # 90% success rate
            cursor.execute("""
                INSERT INTO processing_stages 
                (extraction_id, stage, success, processing_time, business_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                extraction_id,
                stage,
                success,
                random.uniform(0.1, 2.0),  # Processing time between 0.1 and 2.0 seconds
                business_id,
                datetime.now() - timedelta(days=random.randint(0, 7))
            ))
    
    conn.commit()

def populate_error_logs(conn, templates):
    """Populate error_logs table with test data."""
    cursor = conn.cursor()
    
    error_types = ['validation_error', 'extraction_error', 'processing_error', 'timeout']
    stages = ['preprocessing', 'extraction', 'validation', 'postprocessing']
    endpoints = ['/api/message', '/api/templates', '/api/extraction']
    
    for template in templates:
        for error_type in error_types:
            for stage in stages:
                for _ in range(random.randint(1, 5)):  # 1-5 errors per type per stage
                    cursor.execute("""
                        INSERT INTO error_logs 
                        (timestamp, error_type, error_message, stack_trace, endpoint, stage, processing_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datetime.now() - timedelta(days=random.randint(0, 7)),
                        error_type,
                        f"Test error message for {error_type} in {stage}",
                        "Test stack trace",
                        random.choice(endpoints),
                        stage,
                        random.uniform(0.1, 1.0)  # Processing time between 0.1 and 1.0 seconds
                    ))
    
    conn.commit()

def populate_llm_calls(conn, templates):
    """Populate llm_calls table with test data."""
    cursor = conn.cursor()
    
    # Use the existing business_id
    business_id = 'bc7e1824-49b4-4056-aabe-b045a1f79e3b'
    
    call_types = ['data_extraction', 'classification', 'summarization']
    input_texts = [
        "Please extract contact information from this message",
        "Classify this message as urgent or normal",
        "Summarize the following text",
        "Extract order details from this message",
        "Identify the main topic of this text"
    ]
    
    for template in templates:
        for call_type in call_types:
            for _ in range(random.randint(5, 10)):  # 5-10 calls per type
                cursor.execute("""
                    INSERT INTO llm_calls 
                    (call_id, business_id, input_text, call_type, completion_time, tokens_used, system_prompt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),  # Generate new UUID for call_id
                    business_id,
                    random.choice(input_texts),
                    call_type,
                    random.uniform(0.5, 3.0),  # Completion time between 0.5 and 3.0 seconds
                    random.randint(100, 1000),  # Tokens used between 100 and 1000
                    f"System prompt for {call_type}"
                ))
    
    conn.commit()

def main():
    """Main function to populate all tables."""
    conn = None
    try:
        conn = get_db_connection()
        
        # Populate tables in order
        templates = populate_templates(conn)
        populate_extraction_results(conn, templates)
        populate_processing_stages(conn, templates)
        populate_error_logs(conn, templates)
        populate_llm_calls(conn, templates)
        
        print("Successfully populated test data")
        
    except Exception as e:
        print(f"Error populating test data: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 