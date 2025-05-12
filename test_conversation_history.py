#!/usr/bin/env python
import sys
import os
import logging
from datetime import datetime
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.standard_variables import provide_conversation_history
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_conversation_history(user_id=None):
    # Test parameters
    default_user_id = "2c50e7a1-e9bf-43ef-8450-fcf3b0354c96"
    business_id = "bc7e1824-49b4-4056-aabe-b045a1f79e3b"
    api_key = "cd0fd3314e8f1fe7cef737db4ac21778ccc7d5a97bbb33d9af17612e337231d6"
    user_id = user_id or default_user_id
    log.info(f"Using user_id: {user_id}")
    
    # Get database connection
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
            
        # First, verify the business exists and get a conversation_id
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.conversation_id 
            FROM conversations c
            JOIN businesses b ON c.business_id = b.business_id
            WHERE c.business_id = %s 
            AND b.api_key = %s
            AND c.user_id = %s
            LIMIT 1
            """,
            (business_id, api_key, user_id)
        )
        
        result = cursor.fetchone()
        if not result:
            log.error("No conversations found for the given business_id and api_key")
            return
            
        conversation_id = result['conversation_id']
        log.info(f"Found conversation_id: {conversation_id}")
        
        # Test conversation history with different options
        log.info("\nTesting conversation history with default options:")
        history = provide_conversation_history(conn, conversation_id)
        print(history)
        
        log.info("\nTesting conversation history with timestamps:")
        history_with_timestamps = provide_conversation_history(
            conn, 
            conversation_id, 
            include_timestamps=True
        )
        print(history_with_timestamps)
        
        log.info("\nTesting conversation history with limited messages:")
        history_limited = provide_conversation_history(
            conn, 
            conversation_id, 
            max_messages=5
        )
        print(history_limited)
        
    except Exception as e:
        log.error(f"Error during test: {str(e)}", exc_info=True)
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test conversation history for a user.")
    parser.add_argument('--user_id', type=str, help='User ID to test (optional)')
    args = parser.parse_args()
    test_conversation_history(user_id=args.user_id) 