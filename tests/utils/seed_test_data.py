#!/usr/bin/env python3
"""
Script for seeding test data into the test schema.
This script populates the test schema with initial data for testing.
"""

import os
import sys
import psycopg2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'name': os.environ.get('DB_NAME', 'icmp_db'),
    'user': os.environ.get('DB_USER', 'icmp_user'),
    'password': os.environ.get('DB_PASSWORD', 'your_password'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}

def connect_to_db():
    """Connect to the database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['name'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        log.error(f"Error connecting to database: {str(e)}")
        raise

def seed_test_data():
    """Seed the test schema with initial data."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Insert test businesses
        cursor.execute("""
            INSERT INTO test.businesses (name, description, created_at, updated_at)
            VALUES 
                ('Test Business 1', 'A test business for development', NOW(), NOW()),
                ('Test Business 2', 'Another test business', NOW(), NOW())
            RETURNING id;
        """)
        business_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(business_ids)} test businesses")
        
        # Insert test stages
        cursor.execute("""
            INSERT INTO test.stages (name, description, business_id, created_at, updated_at)
            VALUES 
                ('Lead', 'Initial contact stage', %s, NOW(), NOW()),
                ('Qualified', 'Qualified lead stage', %s, NOW(), NOW())
            RETURNING id;
        """, (business_ids[0], business_ids[0]))
        stage_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(stage_ids)} test stages")
        
        # Insert test templates
        cursor.execute("""
            INSERT INTO test.templates (name, content, stage_id, created_at, updated_at)
            VALUES 
                ('Welcome Template', 'Welcome to our service!', %s, NOW(), NOW()),
                ('Follow-up Template', 'Thank you for your interest', %s, NOW(), NOW())
            RETURNING id;
        """, (stage_ids[0], stage_ids[1]))
        template_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(template_ids)} test templates")
        
        # Insert test agents
        cursor.execute("""
            INSERT INTO test.agents (name, email, business_id, created_at, updated_at)
            VALUES 
                ('Test Agent 1', 'agent1@test.com', %s, NOW(), NOW()),
                ('Test Agent 2', 'agent2@test.com', %s, NOW(), NOW())
            RETURNING id;
        """, (business_ids[0], business_ids[1]))
        agent_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(agent_ids)} test agents")
        
        # Insert test users
        cursor.execute("""
            INSERT INTO test.users (name, email, business_id, created_at, updated_at)
            VALUES 
                ('Test User 1', 'user1@test.com', %s, NOW(), NOW()),
                ('Test User 2', 'user2@test.com', %s, NOW(), NOW())
            RETURNING id;
        """, (business_ids[0], business_ids[1]))
        user_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(user_ids)} test users")
        
        # Insert test conversations
        cursor.execute("""
            INSERT INTO test.conversations (user_id, agent_id, stage_id, created_at, updated_at)
            VALUES 
                (%s, %s, %s, NOW(), NOW()),
                (%s, %s, %s, NOW(), NOW())
            RETURNING id;
        """, (user_ids[0], agent_ids[0], stage_ids[0], user_ids[1], agent_ids[1], stage_ids[1]))
        conversation_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(conversation_ids)} test conversations")
        
        # Insert test messages
        cursor.execute("""
            INSERT INTO test.messages (conversation_id, content, sender_type, created_at, updated_at)
            VALUES 
                (%s, 'Hello, this is a test message', 'user', NOW(), NOW()),
                (%s, 'Thank you for your message', 'agent', NOW(), NOW())
            RETURNING id;
        """, (conversation_ids[0], conversation_ids[0]))
        message_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(message_ids)} test messages")
        
        # Insert test LLM calls
        cursor.execute("""
            INSERT INTO test.llm_calls (message_id, prompt, response, created_at, updated_at)
            VALUES 
                (%s, 'Test prompt 1', 'Test response 1', NOW(), NOW()),
                (%s, 'Test prompt 2', 'Test response 2', NOW(), NOW())
            RETURNING id;
        """, (message_ids[0], message_ids[1]))
        llm_call_ids = [row[0] for row in cursor.fetchall()]
        log.info(f"Created {len(llm_call_ids)} test LLM calls")
        
        log.info("Test data seeding completed successfully")
        
    except Exception as e:
        log.error(f"Error seeding test data: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    log.info("Starting test data seeding...")
    try:
        seed_test_data()
        log.info("Test data seeding completed successfully.")
    except Exception as e:
        log.error(f"Test data seeding failed: {str(e)}")
        sys.exit(1) 