# backend/routes/message_handling.py
from flask import jsonify, request, Blueprint, current_app
import uuid
import logging
import json
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection, get_db_pool
from openai_helper import call_openai
from auth import require_business_api_key
import re

log = logging.getLogger(__name__)

bp = Blueprint('message_handling', __name__)

message_schema = {
    "type": "object",
    "properties": {
        "business_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string"},
        "message": {"type": "string"},
        "conversation_id": {"type": "string", "format": "uuid"},
        "agent_id": {"type": "string", "format": "uuid"},
        "session_id": {"type": "string"}
    },
    "required": ["business_id", "user_id", "message"]
}

def handle_message_route(request, schemas, get_db_connection, call_openai):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    try:
        validate(instance=data, schema=message_schema)
        user_id = data['user_id']
        business_id = data['business_id']
        message_text = data['message']
        session_id = data.get('session_id') # Optional
        conversation_id = data.get('conversation_id') # Get conversation_id if provided
        agent_id = data.get('agent_id') # Get agent_id if provided

        log.info(f"Handling message for user {user_id}, business {business_id}")

        # Create message data dictionary for the MessageHandler
        message_data = {
            'business_id': business_id,
            'user_id': user_id,
            'content': message_text
        }
        
        # Add optional fields if they exist
        if conversation_id:
            message_data['conversation_id'] = conversation_id
        if agent_id:
            message_data['agent_id'] = agent_id

        # Get a connection from the pool
        conn = get_db_connection()
        try:
            # Import the MessageHandler here to avoid circular imports
            from backend.message_processing.message_handler import MessageHandler
            
            # Create a MessageHandler instance with a connection pool
            message_handler = MessageHandler(get_db_pool())
            
            # Process the message
            result = message_handler.process_message(message_data)
            
            if result.get('success'):
                # Return the actual response from the MessageHandler
                return jsonify({
                    'success': True,
                    'response': result.get('response', ''),
                    'conversation_id': result.get('conversation_id', ''),
                    'message_id': result.get('message_id', ''),
                    'response_id': result.get('response_id', ''),
                    'process_log_id': result.get('process_log_id', ''),
                    'processing_steps': result.get('processing_steps', []),
                    # Add a chat_window field for the frontend
                    'chat_window': {
                        'user_message': {
                            'id': result.get('message_id', ''),
                            'content': message_text,
                            'timestamp': result.get('created_at', ''),
                            'status': 'delivered'
                        },
                        'ai_response': {
                            'id': result.get('response_id', ''),
                            'content': result.get('response', ''),
                            'timestamp': result.get('created_at', ''),
                            'status': 'delivered'
                        }
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }), 500

        except Exception as e:
            log.error(f"Error processing message: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error processing message: {str(e)}"
            }), 500
        finally:
            if conn:
                release_db_connection(conn)

    except ValidationError as e:
        log.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Validation error: {str(e)}"
        }), 400
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }), 500

@bp.route('/message', methods=['POST', 'OPTIONS'])
@require_business_api_key
#@limiter.limit("30 per minute")
def handle_message():
    # The OPTIONS method is handled by the @require_business_api_key decorator.
    # We only need to handle the POST request here.
    
    # Handle the POST request
    schemas = current_app.config['SCHEMAS']
    return handle_message_route(request, schemas, get_db_connection, call_openai)

@bp.route('/message/logs/<log_id>', methods=['GET'])
@require_business_api_key
def get_message_log(log_id):
    """Get detailed processing log for a message."""
    try:
        from backend.message_processing.message_handler import MessageHandler
        
        # Get business_id from query parameters
        business_id = request.args.get('business_id')
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
        
        message_handler = MessageHandler(get_db_pool())
        process_log = message_handler.get_process_log(log_id)
        
        if not process_log:
            return jsonify({"error": "Process log not found"}), 404
        
        # Verify the log belongs to the requesting business
        if process_log.get('business_id') != business_id:
            return jsonify({"error": "Process log not found for this business"}), 404
        
        return jsonify(process_log)
    
    except Exception as e:
        log.error(f"Error retrieving process log: {str(e)}")
        return jsonify({"error": f"Error retrieving process log: {str(e)}"}), 500

@bp.route('/message/logs/recent', methods=['GET'])
@require_business_api_key
def get_recent_logs():
    """Get recent message processing logs."""
    try:
        from backend.message_processing.message_handler import MessageHandler
        
        business_id = request.args.get('business_id')
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
        
        limit = int(request.args.get('limit', 10))
        
        message_handler = MessageHandler(get_db_pool())
        logs = message_handler.get_recent_process_logs(business_id, limit)
        
        return jsonify(logs)
    
    except Exception as e:
        log.error(f"Error retrieving recent logs: {str(e)}")
        return jsonify({"error": f"Error retrieving recent logs: {str(e)}"}), 500

# register_message_routes seems unnecessary if using Blueprints directly in app.py
# def register_message_routes(app, require_api_key, limiter):
#     app.register_blueprint(bp)