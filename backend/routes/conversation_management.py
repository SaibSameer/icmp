"""
Conversation management module.

This module provides endpoints for managing conversations, including
retrieving conversation history, updating conversation data, and
managing conversation state.
"""

from flask import Blueprint, jsonify, request
import logging
import uuid
from db import get_db_connection, release_db_connection
from auth import require_business_api_key
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)

# Create blueprint for conversation endpoints
conversation_bp = Blueprint('conversations', __name__)

# Remove the test route
# @conversation_bp.route('/test', methods=['GET'])
# def test_route():
#     return jsonify({"message": "Conversation blueprint test route OK"}), 200

@conversation_bp.route('/', methods=['GET', 'OPTIONS'])
@require_business_api_key
def get_conversations():
    """
    Get all conversations for the authenticated business.
    
    Query Parameters:
        business_id: (Required) The business ID to filter conversations by
    """
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error": "business_id parameter is required"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query based only on business_id, join with users table
            cursor.execute("""
                SELECT 
                    c.conversation_id, 
                    c.business_id, 
                    c.user_id, 
                    c.session_id, 
                    c.start_time, 
                    c.last_updated, 
                    c.stage_id,
                    u.first_name, -- Get user's first name
                    u.last_name   -- Get user's last name
                FROM conversations c
                LEFT JOIN users u ON c.user_id = u.user_id
                WHERE c.business_id = %s
                ORDER BY c.last_updated DESC;
            """, (business_id,))
            
            conversations = cursor.fetchall()
            
            # If no conversations found, return empty list
            if not conversations:
                return jsonify([]), 200
            
            # Get messages for each conversation
            for conv in conversations:
                cursor.execute("""
                    SELECT 
                        message_id, 
                        conversation_id, 
                        user_id, 
                        sender_type as sender, 
                        message_content as content, 
                        created_at as timestamp
                    FROM messages 
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC;
                """, (conv['conversation_id'],))
                
                messages = cursor.fetchall()
                conv['messages'] = messages if messages else []
            
            # Convert UUIDs and datetime objects to strings
            for conv in conversations:
                conv['conversation_id'] = str(conv['conversation_id'])
                conv['business_id'] = str(conv['business_id'])
                conv['user_id'] = str(conv['user_id'])
                # Handle potentially null first/last names (though join should handle this)
                conv['user_name'] = f"{conv.get('first_name', '')} {conv.get('last_name', '')}".strip() 
                if conv['session_id']:
                    conv['session_id'] = str(conv['session_id'])
                if conv['stage_id']:
                    conv['stage_id'] = str(conv['stage_id'])
                conv['start_time'] = conv['start_time'].isoformat() if conv['start_time'] else None
                conv['last_updated'] = conv['last_updated'].isoformat() if conv['last_updated'] else None
                
                # Convert message fields too
                for msg in conv['messages']:
                    msg['message_id'] = str(msg['message_id'])
                    msg['conversation_id'] = str(msg['conversation_id'])
                    msg['user_id'] = str(msg['user_id'])
                    msg['timestamp'] = msg['timestamp'].isoformat() if msg['timestamp'] else None
            
            return jsonify(conversations), 200
    
    except Exception as e:
        log.error(f"Error retrieving conversations: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve conversations: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@conversation_bp.route('/<uuid:conversation_id>', methods=['DELETE', 'OPTIONS'])
@require_business_api_key
def delete_conversation(conversation_id):
    """
    Delete a conversation and all associated messages.
    
    Args:
        conversation_id: The ID of the conversation to delete
    """
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error": "business_id parameter is required"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # First, verify the conversation belongs to the business
            cursor.execute("""
                SELECT 1 FROM conversations 
                WHERE conversation_id = %s AND business_id = %s
            """, (conversation_id, business_id))
            
            if not cursor.fetchone():
                return jsonify({"error": "Conversation not found or not authorized"}), 404
            
            # Delete messages first (due to foreign key constraints)
            cursor.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
            message_count = cursor.rowcount
            
            # Then delete the conversation
            cursor.execute("DELETE FROM conversations WHERE conversation_id = %s", (conversation_id,))
            
            conn.commit()
            
            return jsonify({
                "message": f"Conversation deleted successfully with {message_count} messages",
                "conversation_id": conversation_id
            }), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error deleting conversation: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to delete conversation: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@conversation_bp.route('/reassign', methods=['POST', 'OPTIONS'])
@require_business_api_key
def reassign_conversations():
    """
    Reassign conversations from one stage to another.
    
    Request Body:
        source_stage_id: The ID of the stage to reassign conversations from
        target_stage_id: The ID of the stage to reassign conversations to
        business_id: The business ID to ensure authorization
    """
    data = request.get_json()
    
    # Validate request data
    source_stage_id = data.get('source_stage_id')
    target_stage_id = data.get('target_stage_id')
    business_id = data.get('business_id')
    
    # Also check for business_id in query params (frontend sends it both ways)
    if not business_id:
        business_id = request.args.get('business_id')
        
    if not source_stage_id or not target_stage_id or not business_id:
        return jsonify({
            "error_code": "BAD_REQUEST", 
            "message": "Missing required fields: source_stage_id, target_stage_id, and business_id are required"
        }), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # First, verify the stages belong to the business
            cursor.execute("""
                SELECT stage_id FROM stages 
                WHERE stage_id IN (%s, %s) AND business_id = %s
            """, (source_stage_id, target_stage_id, business_id))
            
            found_stages = cursor.fetchall()
            if len(found_stages) != 2:
                return jsonify({
                    "error_code": "NOT_FOUND",
                    "message": "One or both stages not found or not authorized"
                }), 404
            
            # Update conversations from source stage to target stage
            cursor.execute("""
                UPDATE conversations 
                SET stage_id = %s, last_updated = NOW()
                WHERE stage_id = %s AND business_id = %s
                RETURNING conversation_id
            """, (target_stage_id, source_stage_id, business_id))
            
            updated_conversations = cursor.fetchall()
            update_count = len(updated_conversations)
            
            conn.commit()
            
            return jsonify({
                "message": f"Successfully reassigned {update_count} conversations from stage {source_stage_id} to stage {target_stage_id}",
                "updated_conversations": [str(conv['conversation_id']) for conv in updated_conversations],
                "count": update_count
            }), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error reassigning conversations: {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": f"Failed to reassign conversations: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)