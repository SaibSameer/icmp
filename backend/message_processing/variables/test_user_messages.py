#!/usr/bin/env python
import os
import sys
import argparse
import logging

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

from backend.db import get_db_connection, release_db_connection
from backend.message_processing.variables.user_messages import provide_user_messages

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def check_database_state(conn, business_id, user_id):
    """Check the state of relevant tables in the database"""
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    log.info(f"User found: {user is not None}")
    
    # Check businesses table
    cursor.execute("SELECT * FROM businesses WHERE business_id = %s", (business_id,))
    business = cursor.fetchone()
    log.info(f"Business found: {business is not None}")
    
    # Check conversations table
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM conversations 
        WHERE user_id = %s AND business_id = %s
    """, (user_id, business_id))
    conv_count = cursor.fetchone()['count']
    log.info(f"Conversations found: {conv_count}")
    
    # Check messages table
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE user_id = %s
    """, (user_id,))
    msg_count = cursor.fetchone()['count']
    log.info(f"Total messages found: {msg_count}")
    
    # Show some sample messages if they exist
    if msg_count > 0:
        cursor.execute("""
            SELECT m.*, c.conversation_id 
            FROM messages m
            LEFT JOIN conversations c ON m.user_id = c.user_id
            WHERE m.user_id = %s
            LIMIT 5
        """, (user_id,))
        sample_messages = cursor.fetchall()
        log.info("Sample messages:")
        for msg in sample_messages:
            log.info(f"Message: {msg}")

def test_user_messages(business_id, user_id, max_messages=50, include_timestamps=False, include_conversation_id=False):
    conn = None
    try:
        log.info(f"Testing with business_id: {business_id}, user_id: {user_id}")
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        
        # Check database state first
        check_database_state(conn, business_id, user_id)
        
        value = provide_user_messages(
            conn=conn,
            user_id=user_id,
            business_id=business_id,
            max_messages=max_messages,
            include_timestamps=include_timestamps,
            include_conversation_id=include_conversation_id
        )
        print(f"\nUser Messages:")
        print("------------")
        print(value)
    except Exception as e:
        log.error(f"Error testing user_messages: {str(e)}", exc_info=True)
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the user_messages variable provider.")
    parser.add_argument('--business_id', type=str, help='Business ID')
    parser.add_argument('--user_id', type=str, help='User ID')
    parser.add_argument('--max_messages', type=int, default=50, help='Max messages to retrieve (optional)')
    parser.add_argument('--include_timestamps', action='store_true', help='Include timestamps (optional)')
    parser.add_argument('--include_conversation_id', action='store_true', help='Include conversation IDs (optional)')
    
    args = parser.parse_args()

    # Get required parameters from command line or prompt
    business_id = args.business_id or input('Enter Business ID: ')
    user_id = args.user_id or input('Enter User ID: ')

    test_user_messages(
        business_id=business_id,
        user_id=user_id,
        max_messages=args.max_messages,
        include_timestamps=args.include_timestamps,
        include_conversation_id=args.include_conversation_id
    ) 