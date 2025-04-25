#!/usr/bin/env python3
"""
Script to delete all conversation and message records from the system.
This script will:
1. Delete all messages from the messages table
2. Delete all conversations from the conversations table
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

def get_record_counts(conn):
    """
    Get the current count of conversations and messages.
    
    Args:
        conn: Database connection
        
    Returns:
        Tuple of (conversation_count, message_count)
    """
    cursor = conn.cursor()
    
    # Get conversation count
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conversation_count = cursor.fetchone()[0]
    
    # Get message count
    cursor.execute("SELECT COUNT(*) FROM messages")
    message_count = cursor.fetchone()[0]
    
    return conversation_count, message_count

def delete_all_records(conn):
    """
    Delete all records from the messages and conversations tables.
    
    Args:
        conn: Database connection
        
    Returns:
        Tuple of (deleted_conversation_count, deleted_message_count)
    """
    cursor = conn.cursor()
    
    # Get counts before deletion
    before_conv_count, before_msg_count = get_record_counts(conn)
    
    # Delete all messages first (due to foreign key constraints)
    cursor.execute("DELETE FROM messages")
    deleted_message_count = cursor.rowcount
    
    # Delete all conversations
    cursor.execute("DELETE FROM conversations")
    deleted_conversation_count = cursor.rowcount
    
    # Commit the transaction
    conn.commit()
    
    return deleted_conversation_count, deleted_message_count

def main():
    """Main function to delete all conversation and message records."""
    conn = None
    try:
        log.info("Starting database cleanup process...")
        
        # Get database connection
        conn = get_db_connection()
        
        # Get current record counts
        conversation_count, message_count = get_record_counts(conn)
        
        if conversation_count == 0 and message_count == 0:
            log.info("No records found. Database is already clean.")
            return
        
        # Log current counts
        log.info(f"Current record counts:")
        log.info(f"- Conversations: {conversation_count}")
        log.info(f"- Messages: {message_count}")
        
        # Confirm deletion
        response = input("\nWARNING: This will delete ALL conversations and messages from the database.\n"
                         "This action cannot be undone. Are you sure you want to continue? (yes/no): ")
        
        if response.lower() != 'yes':
            log.info("Database cleanup cancelled by user.")
            return
        
        # Delete all records
        deleted_conv_count, deleted_msg_count = delete_all_records(conn)
        
        # Log results
        log.info(f"Database cleanup completed successfully:")
        log.info(f"- Deleted {deleted_conv_count} conversations")
        log.info(f"- Deleted {deleted_msg_count} messages")
        
    except Exception as e:
        log.error(f"Error during database cleanup: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            release_db_connection(conn)
            log.info("Database connection closed.")

if __name__ == "__main__":
    main()