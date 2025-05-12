from flask import Blueprint, request, jsonify
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_api_key

bp = Blueprint('user_stats', __name__, url_prefix='/api/user-stats')

@bp.route('/message-counts', methods=['GET'])
@require_api_key
def get_user_message_counts():
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({'error': 'Missing business_id'}), 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT m.user_id, COUNT(*) as message_count
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.conversation_id
            WHERE c.business_id = %s
            GROUP BY m.user_id
            ''',
            (business_id,)
        )
        results = cursor.fetchall()
        data = [{'user_id': str(row[0]), 'message_count': row[1]} for row in results]
        return jsonify(data)
    finally:
        release_db_connection(conn) 