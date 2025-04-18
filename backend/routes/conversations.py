from flask import Blueprint, request, jsonify, current_app
import logging
from db import get_db_connection, execute_query, release_db_connection
from auth import require_business_api_key
from routes.utils import is_valid_uuid
import json

log = logging.getLogger(__name__)

bp = Blueprint('conversations_bp', __name__, url_prefix='/conversations')

@bp.route('/<user_id>', methods=['GET'])
@require_business_api_key
def get_conversations(user_id):
    if not is_valid_uuid(user_id):
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid user_id format"}), 400

    # Ensure business_id is available either from query params or URL
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Business ID is required"}), 400

    try:
        conn = get_db_connection()
        # Fetch conversation metadata
        conv_query = """
            SELECT conversation_id, business_id, user_id, agent_id, stage_id, session_id, start_time, last_updated, status, created_at, llm_call_id, conversation_summary
            FROM conversations 
            WHERE user_id = %s AND business_id = %s
            ORDER BY last_updated DESC; -- Order by most recent first
        """
        conv_cursor = execute_query(conn, conv_query, (user_id, business_id))
        conv_rows = conv_cursor.fetchall()
        
        conversations_data = []
        if conv_rows:
            conversation_ids = [row['conversation_id'] for row in conv_rows]
            
            # Fetch messages for these conversations
            messages_query = """
                SELECT conversation_id, sender_type, message_content, created_at
                FROM messages
                WHERE conversation_id = ANY(%s::uuid[]) -- Cast the array parameter to uuid[]
                ORDER BY created_at ASC; -- Order messages chronologically
            """
            # Use list(conversation_ids) directly for psycopg2 parameter binding
            messages_cursor = execute_query(conn, messages_query, (list(conversation_ids),))
            message_rows = messages_cursor.fetchall()
            
            # Group messages by conversation_id
            messages_by_conv = {}
            for msg_row in message_rows:
                conv_id_str = str(msg_row['conversation_id'])
                if conv_id_str not in messages_by_conv:
                    messages_by_conv[conv_id_str] = []
                messages_by_conv[conv_id_str].append({
                    "sender": msg_row['sender_type'],
                    "content": msg_row['message_content'],
                    "timestamp": msg_row['created_at'].isoformat()
                })

            # Construct the final response
            for conv_row in conv_rows:
                conv_id_str = str(conv_row["conversation_id"])
                conversations_data.append({
                    "conversation_id": conv_id_str,
                    "business_id": str(conv_row["business_id"]),
                    "user_id": str(conv_row["user_id"]),
                    "agent_id": str(conv_row["agent_id"]) if conv_row["agent_id"] else None,
                    "stage_id": str(conv_row["stage_id"]) if conv_row["stage_id"] else None,
                    "session_id": str(conv_row["session_id"]),
                    "start_time": conv_row["start_time"].isoformat(),
                    "last_updated": conv_row["last_updated"].isoformat(),
                    "status": conv_row["status"],
                    "created_at": conv_row["created_at"].isoformat(),
                    "llm_call_id": conv_row["llm_call_id"],
                    "conversation_summary": json.loads(conv_row["conversation_summary"]) if conv_row["conversation_summary"] else None,
                    "messages": messages_by_conv.get(conv_id_str, []) # Add messages list
                })

        release_db_connection(conn)
        return jsonify(conversations_data), 200
    except Exception as e:
        log.error({"message": "Error in get_conversations", "error": str(e)}, exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500