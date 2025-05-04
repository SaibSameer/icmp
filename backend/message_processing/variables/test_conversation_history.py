#!/usr/bin/env python
import argparse
import logging
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.variables.conversation_history import provide_conversation_history

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_conversation_history(business_id, user_id, conversation_id, max_messages=10, include_timestamps=False):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection")
            return
        value = provide_conversation_history(
            conn=conn,
            conversation_id=conversation_id,
            max_messages=max_messages,
            include_timestamps=include_timestamps
        )
        print(f"Conversation history:\n{value}")
    except Exception as e:
        log.error(f"Error testing conversation_history: {str(e)}", exc_info=True)
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the conversation_history variable provider.")
    parser.add_argument('--business_id', type=str, help='Business ID')
    parser.add_argument('--user_id', type=str, help='User ID')
    parser.add_argument('--conversation_id', type=str, help='Conversation ID')
    parser.add_argument('--max_messages', type=int, default=10, help='Max messages (optional)')
    parser.add_argument('--include_timestamps', action='store_true', help='Include timestamps (optional)')
    args = parser.parse_args()

    business_id = args.business_id or input('Enter Business ID: ')
    user_id = args.user_id or input('Enter User ID: ')
    conversation_id = args.conversation_id or input('Enter Conversation ID: ')

    test_conversation_history(
        business_id=business_id,
        user_id=user_id,
        conversation_id=conversation_id,
        max_messages=args.max_messages,
        include_timestamps=args.include_timestamps
    ) 