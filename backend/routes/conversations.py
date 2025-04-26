from flask import Blueprint, jsonify, request
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_api_key
import logging

# Set up logging
log = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('conversations', __name__, url_prefix='/conversations')

@bp.route('/<user_id>', methods=['GET'])
@require_api_key
def get_conversations(user_id):
    """Get all conversations for a user."""
    try:
        business_id = request.args.get('business_id')
        if not business_id:
            return jsonify({'error': 'business_id is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get conversations for the user and business
        query = """
            SELECT 
                c.id,
                c.user_id,
                c.business_id,
                c.message,
                c.sender,
                c.status,
                c.timestamp,
                c.conversation_id
            FROM conversations c
            WHERE c.user_id = %s AND c.business_id = %s
            ORDER BY c.timestamp DESC
        """
        
        cursor.execute(query, (user_id, business_id))
        conversations = cursor.fetchall()

        # Format the response
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                'id': conv[0],
                'user_id': conv[1],
                'business_id': conv[2],
                'message': conv[3],
                'sender': conv[4],
                'status': conv[5],
                'timestamp': conv[6].isoformat() if conv[6] else None,
                'conversation_id': conv[7]
            })

        return jsonify(formatted_conversations)

    except Exception as e:
        log.error(f"Error fetching conversations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if 'conn' in locals():
            release_db_connection(conn)