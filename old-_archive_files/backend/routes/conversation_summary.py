"""
Routes for managing conversation summaries.
"""

from flask import Blueprint, jsonify, request
from db import get_db_connection, release_db_connection
from auth import require_business_api_key
from services.conversation_summary_service import ConversationSummaryService
import logging

log = logging.getLogger(__name__)

bp = Blueprint('conversation_summary', __name__)
summary_service = ConversationSummaryService()

@bp.route('/conversations/<conversation_id>/summary', methods=['GET'])
@require_business_api_key
def get_conversation_summary(conversation_id):
    """
    Get the summary for a specific conversation.
    
    Args:
        conversation_id: UUID of the conversation
        
    Returns:
        JSON response with the conversation summary
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversation data
        cursor.execute(
            """
            SELECT c.*, b.business_name, u.first_name, u.last_name
            FROM conversations c
            JOIN businesses b ON c.business_id = b.business_id
            JOIN users u ON c.user_id = u.user_id
            WHERE c.conversation_id = %s
            """,
            (conversation_id,)
        )
        conversation = cursor.fetchone()
        
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
            
        # Get messages
        cursor.execute(
            """
            SELECT sender_type, message_content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            """,
            (conversation_id,)
        )
        messages = cursor.fetchall()
        
        # Prepare conversation data
        conversation_data = {
            "business_name": conversation['business_name'],
            "user_name": f"{conversation['first_name']} {conversation['last_name']}",
            "conversation_id": str(conversation['conversation_id']),
            "start_time": conversation['start_time'].isoformat(),
            "last_updated": conversation['last_updated'].isoformat(),
            "conversation_history": [
                {
                    "sender": msg['sender_type'],
                    "content": msg['message_content'],
                    "timestamp": msg['created_at'].isoformat()
                }
                for msg in messages
            ]
        }
        
        # Generate summary
        summary = summary_service.generate_summary(conversation_data)
        
        # Save summary to database
        summary_service.save_summary(conn, conversation_id, summary)
        
        return jsonify(summary), 200
        
    except Exception as e:
        log.error(f"Error getting conversation summary: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/conversations/<conversation_id>/summary', methods=['POST'])
@require_business_api_key
def generate_conversation_summary(conversation_id):
    """
    Generate and save a new summary for a conversation.
    
    Args:
        conversation_id: UUID of the conversation
        
    Returns:
        JSON response with the generated summary
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversation data
        cursor.execute(
            """
            SELECT c.*, b.business_name, u.first_name, u.last_name
            FROM conversations c
            JOIN businesses b ON c.business_id = b.business_id
            JOIN users u ON c.user_id = u.user_id
            WHERE c.conversation_id = %s
            """,
            (conversation_id,)
        )
        conversation = cursor.fetchone()
        
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
            
        # Get messages
        cursor.execute(
            """
            SELECT sender_type, message_content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            """,
            (conversation_id,)
        )
        messages = cursor.fetchall()
        
        # Prepare conversation data
        conversation_data = {
            "business_name": conversation['business_name'],
            "user_name": f"{conversation['first_name']} {conversation['last_name']}",
            "conversation_id": str(conversation['conversation_id']),
            "start_time": conversation['start_time'].isoformat(),
            "last_updated": conversation['last_updated'].isoformat(),
            "conversation_history": [
                {
                    "sender": msg['sender_type'],
                    "content": msg['message_content'],
                    "timestamp": msg['created_at'].isoformat()
                }
                for msg in messages
            ]
        }
        
        # Generate new summary
        summary = summary_service.generate_summary(conversation_data)
        
        # Save summary to database
        if summary_service.save_summary(conn, conversation_id, summary):
            return jsonify(summary), 200
        else:
            return jsonify({"error": "Failed to save summary"}), 500
        
    except Exception as e:
        log.error(f"Error generating conversation summary: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        if conn:
            release_db_connection(conn)