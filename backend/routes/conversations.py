from flask import Blueprint, request, jsonify, g
import logging
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_internal_key

# Set up logging
log = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

@bp.route('', methods=['GET'])
@require_internal_key
def get_conversations():
    # Get business_id from context
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Fetching conversations for business {business_id}")

    # Optional filters (e.g., user_id, status)
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT conversation_id, user_id, agent_id, stage_id, session_id, 
                   start_time, last_updated, status 
            FROM conversations 
            WHERE business_id = %s 
        """
        params = [business_id]

        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY last_updated DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        conversations_list = [
            {
                "conversation_id": str(row[0]),
                "user_id": str(row[1]),
                "agent_id": str(row[2]) if row[2] else None,
                "stage_id": str(row[3]) if row[3] else None,
                "session_id": row[4],
                "start_time": row[5].isoformat() if row[5] else None,
                "last_updated": row[6].isoformat() if row[6] else None,
                "status": row[7]
            } for row in rows
        ]
        return jsonify(conversations_list), 200

    except Exception as e:
        log.error(f"Error fetching conversations for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)