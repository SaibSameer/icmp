"""
Conversation management module.

This module provides endpoints for managing conversations, including
retrieving conversation history, updating conversation data, and
managing conversation state. It also includes the primary endpoint
for processing incoming messages via the API.
"""

from flask import Blueprint, jsonify, request, g
import logging
import uuid
import json # Added for parsing message data
from backend.db import get_db_connection, release_db_connection, get_db_pool # Added get_db_pool
from backend.auth import require_internal_key, require_api_key
from psycopg2.extras import RealDictCursor
from backend.message_processing.message_handler import MessageHandler # Import MessageHandler
from backend.message_processing.ai_control_service import ai_control_service # Import AI control service
from backend.utils import is_valid_uuid # Import utility
from datetime import timedelta

log = logging.getLogger(__name__)

# Create blueprint for conversation endpoints - REMOVED url_prefix
conversation_bp = Blueprint('conversations', __name__)

# Remove the test route
# @conversation_bp.route('/test', methods=['GET'])
# def test_route():
#     return jsonify({"message": "Conversation blueprint test route OK"}), 200

@conversation_bp.route('/conversations', methods=['GET', 'OPTIONS'])
@require_api_key
def get_conversations():
    """
    Get all conversations, requires admin key.
    Optionally filter by business_id query parameter.
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Get optional business_id filter from query parameter
    business_id_filter = request.args.get('business_id')
    if business_id_filter and not is_valid_uuid(business_id_filter):
         return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in query parameter"}), 400
    
    log_msg = "Fetching all conversations (admin)"
    if business_id_filter:
        log_msg += f" filtered by business_id={business_id_filter}"
    log.info(log_msg)
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            params = []
            base_query = """
                SELECT 
                    c.conversation_id, 
                    c.business_id, 
                    c.user_id, 
                    c.session_id, 
                    c.start_time, 
                    c.last_updated, 
                    c.stage_id,
                    u.first_name,
                    u.last_name,
                    COALESCE(
                        (
                            SELECT json_agg(
                                json_build_object(
                                    'message_id', m.message_id,
                                    'content', m.message_content,
                                    'message_content', m.message_content,
                                    'sender_type', m.sender_type,
                                    'timestamp', m.created_at,
                                    'is_from_agent', CASE WHEN m.sender_type = 'assistant' THEN true ELSE false END
                                ) ORDER BY m.created_at ASC
                            )
                            FROM messages m
                            WHERE m.conversation_id = c.conversation_id
                        ),
                        '[]'::json
                    ) as messages
                FROM conversations c
                LEFT JOIN users u ON c.user_id = u.user_id
            """
            
            where_clauses = []
            if business_id_filter:
                where_clauses.append("c.business_id = %s")
                params.append(business_id_filter)
                
            if where_clauses:
                query = base_query + " WHERE " + " AND ".join(where_clauses)
            else:
                query = base_query
                
            query += " GROUP BY c.conversation_id, c.business_id, c.user_id, c.session_id, c.start_time, c.last_updated, c.stage_id, u.first_name, u.last_name"
            query += " ORDER BY c.last_updated DESC;"
            
            cursor.execute(query, tuple(params))
            
            conversations = cursor.fetchall()
            
            # If no conversations found, return empty list
            if not conversations:
                response = jsonify([])
                response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
                response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
                return response, 200
            
            # Process conversations and messages
            for conv in conversations:
                conv['conversation_id'] = str(conv['conversation_id'])
                conv['business_id'] = str(conv['business_id'])
                conv['user_id'] = str(conv['user_id'])
                conv['user_name'] = f"{conv.get('first_name', '')} {conv.get('last_name', '')}".strip()
                if conv['session_id']:
                    conv['session_id'] = str(conv['session_id'])
                if conv['stage_id']:
                    conv['stage_id'] = str(conv['stage_id'])
                conv['start_time'] = conv['start_time'].isoformat() if conv['start_time'] else None
                conv['last_updated'] = conv['last_updated'].isoformat() if conv['last_updated'] else None
                
                # Process messages
                messages = conv.get('messages', [])
                if messages and messages[0] is not None:  # Check if there are any messages
                    for msg in messages:
                        msg['message_id'] = str(msg['message_id'])
                        # Only call isoformat if timestamp is a datetime object
                        if msg['timestamp'] and not isinstance(msg['timestamp'], str):
                            msg['timestamp'] = msg['timestamp'].isoformat()
                else:
                    conv['messages'] = []
                
                # Add message summary
                if messages and messages[0] is not None:
                    user_messages = [msg for msg in messages if not msg['is_from_agent']]
                    agent_messages = [msg for msg in messages if msg['is_from_agent']]
                    
                    conv['message_summary'] = {
                        'total_messages': len(messages),
                        'user_messages': len(user_messages),
                        'agent_messages': len(agent_messages),
                        'last_user_message': user_messages[-1]['message_content'] if user_messages else None,
                        'last_agent_message': agent_messages[-1]['message_content'] if agent_messages else None,
                        'last_message_time': messages[-1]['timestamp'] if messages else None
                    }
                else:
                    conv['message_summary'] = {
                        'total_messages': 0,
                        'user_messages': 0,
                        'agent_messages': 0,
                        'last_user_message': None,
                        'last_agent_message': None,
                        'last_message_time': None
                    }
            
            response = jsonify(conversations)
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200
    
    except Exception as e:
        log.error(f"Error retrieving conversations: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve conversations: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@conversation_bp.route('/<uuid:conversation_id>', methods=['DELETE', 'OPTIONS'])
@require_internal_key
def delete_conversation(conversation_id):
    """
    Delete a conversation and all associated messages.
    Assumes business context (g.business_id) is set by the decorator.
    """
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Attempting to delete conversation {conversation_id} for business {business_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Verify conversation belongs to business using context business_id
            cursor.execute("""
                SELECT 1 FROM conversations 
                WHERE conversation_id = %s AND business_id = %s
            """, (conversation_id, business_id))
            
            if not cursor.fetchone():
                log.warning(f"Conversation {conversation_id} not found or not authorized for business {business_id}")
                return jsonify({"error": "Conversation not found or not authorized"}), 404
            
            # Delete messages first
            cursor.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
            message_count = cursor.rowcount
            log.info(f"Deleted {message_count} messages for conversation {conversation_id}")
            
            # Then delete the conversation
            cursor.execute("DELETE FROM conversations WHERE conversation_id = %s", (conversation_id,))
            
            conn.commit()
            log.info(f"Deleted conversation {conversation_id} for business {business_id}")
            
            return jsonify({
                "message": f"Conversation deleted successfully with {message_count} messages",
                "conversation_id": str(conversation_id) # Return string UUID
            }), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error deleting conversation {conversation_id} for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to delete conversation: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@conversation_bp.route('/reassign', methods=['POST', 'OPTIONS'])
@require_internal_key
def reassign_conversations():
    """
    Reassign conversations from one stage to another.
    Assumes business context (g.business_id) is set by the decorator.
    """
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id

    data = request.get_json()
    if not data:
         return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400
    
    source_stage_id = data.get('source_stage_id')
    target_stage_id = data.get('target_stage_id')
    
    if not source_stage_id or not target_stage_id:
        return jsonify({
            "error_code": "BAD_REQUEST", 
            "message": "Missing required fields: source_stage_id and target_stage_id are required"
        }), 400
    
    log.info(f"Attempting reassignment from stage {source_stage_id} to {target_stage_id} for business {business_id}")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify both stages belong to the business using context business_id
            cursor.execute("""
                SELECT stage_id FROM stages 
                WHERE stage_id IN (%s, %s) AND business_id = %s
            """, (source_stage_id, target_stage_id, business_id))
            
            found_stages = cursor.fetchall()
            if len(found_stages) != 2:
                log.warning(f"Stage verification failed for reassignment by business {business_id}. Stages found: {found_stages}")
                return jsonify({"error_code": "NOT_FOUND", "message": "One or both stages not found or not authorized"}), 404
                
            # Reassign conversations
            cursor.execute("""
                UPDATE conversations 
                SET stage_id = %s 
                WHERE stage_id = %s AND business_id = %s;
            """, (target_stage_id, source_stage_id, business_id))
            
            reassigned_count = cursor.rowcount
            conn.commit()
            log.info(f"Reassigned {reassigned_count} conversations from stage {source_stage_id} to {target_stage_id} for business {business_id}")
            
            return jsonify({
                "success": True,
                "message": f"Successfully reassigned {reassigned_count} conversations",
                "reassigned_count": reassigned_count
            }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error reassigning conversations for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to reassign conversations: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

# --- New Route for Processing Messages ---
@conversation_bp.route('/message', methods=['POST', 'OPTIONS'])
@require_api_key # Use Admin API Key validation
def process_api_message():
    """
    Handles incoming messages sent directly via the API.
    Requires Admin API Key for authentication.
    Expects JSON body: { business_id: uuid, user_id: uuid, message: string }
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    business_id = data.get('business_id')
    user_id = data.get('user_id')
    message_content = data.get('message')

    if not all([business_id, user_id, message_content]):
        missing = [k for k, v in {'business_id': business_id, 'user_id': user_id, 'message': message_content}.items() if not v]
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if not is_valid_uuid(business_id) or not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid UUID format for business_id or user_id"}), 400

    log.info(f"Processing API message for business {business_id} from user {user_id}")

    if not MessageHandler:
        log.error("MessageHandler class not found. Cannot process message.")
        return jsonify({"error": "Message processing component not available"}), 503 # Service Unavailable

    try:
        # Pass the actual db pool object to the handler
        db_pool = get_db_pool() # Call the function to get the pool
        if not db_pool:
            log.error("Failed to get database pool.")
            return jsonify({"error": "Database connection pool unavailable"}), 503
        
        message_handler = MessageHandler(db_pool) # Pass the pool object
        message_data = {
            'business_id': business_id,
            'user_id': user_id,
            'content': message_content,
            'platform': 'api' # Indicate the source is the direct API
        }
        
        # Process the message
        result = message_handler.process_message(message_data)
        
        # Log and return the result
        if result.get('success'):
            log.info(f"Successfully processed API message for business {business_id}. Log ID: {result.get('process_log_id')}")
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200
        else:
            log.error(f"MessageHandler failed for business {business_id}: {result.get('error')}")
            # Ensure a JSON response even on failure
            error_response = {
                "success": False,
                "error": result.get('error', 'Unknown processing error'),
                "process_log_id": result.get('process_log_id') # Include log ID if available
            }
            response = jsonify(error_response)
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 500 # Internal Server Error

    except Exception as e:
        log.error(f"Exception during API message processing for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during message processing"}), 500

# --- New Routes for Fetching Logs ---

@conversation_bp.route('/message/logs/recent', methods=['GET'])
@require_api_key
def get_recent_logs():
    """
    Get recent process logs, requires admin key.
    Requires 'business_id' query parameter.
    """
    business_id = request.args.get('business_id')
    limit = request.args.get('limit', 10, type=int)

    if not business_id:
        return jsonify({"error": "business_id query parameter is required"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error": "Invalid business_id format"}), 400

    log.info(f"Fetching recent logs (limit {limit}) for business {business_id}")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT log_id, business_id, user_id, conversation_id, original_message, start_time
                FROM process_logs
                WHERE business_id = %s
                ORDER BY start_time DESC
                LIMIT %s;
            """, (business_id, limit))
            logs = cursor.fetchall()
            # Convert UUIDs and datetime to strings
            for log_entry in logs:
                for key, value in log_entry.items():
                    if isinstance(value, uuid.UUID):
                        log_entry[key] = str(value)
                    elif hasattr(value, 'isoformat'): # Check for datetime objects
                         log_entry[key] = value.isoformat()
            return jsonify(logs), 200
    except Exception as e:
        log.error(f"Error fetching recent logs for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve recent logs"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@conversation_bp.route('/message/logs/<log_id>', methods=['GET'])
@require_api_key
def get_log_details(log_id):
    """
    Get detailed processing log by ID, requires admin key.
    Requires 'business_id' query parameter for authorization check.
    """
    business_id = request.args.get('business_id')

    if not business_id:
        return jsonify({"error": "business_id query parameter is required"}), 400
    if not is_valid_uuid(business_id):
         return jsonify({"error": "Invalid business_id format"}), 400
    if not is_valid_uuid(log_id): # Also validate log_id
        return jsonify({"error": "Invalid log_id format"}), 400

    log.info(f"Fetching log details for log_id {log_id} requested by business {business_id}")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Fetch the main log entry, ensuring it matches the business_id
            cursor.execute("""
                SELECT * FROM process_logs
                WHERE log_id = %s AND business_id = %s;
            """, (log_id, business_id))
            log_data = cursor.fetchone()

            if not log_data:
                log.warning(f"Log details for log_id {log_id} not found or not authorized for business {business_id}")
                return jsonify({"error": "Log not found or not authorized"}), 404

            # Fetch the processing steps associated with the log
            cursor.execute("""
                SELECT * FROM processing_steps
                WHERE log_id = %s
                ORDER BY timestamp ASC;
            """, (log_id,))
            steps = cursor.fetchall()

            # Combine log data and steps
            log_data['processing_steps'] = steps

            # Convert UUIDs and datetime objects to strings for JSON serialization
            def serialize_log_data(data):
                 if isinstance(data, dict):
                     return {k: serialize_log_data(v) for k, v in data.items()}
                 elif isinstance(data, list):
                     return [serialize_log_data(item) for item in data]
                 elif isinstance(data, uuid.UUID):
                     return str(data)
                 elif hasattr(data, 'isoformat'): # Check for datetime
                     return data.isoformat()
                 elif isinstance(data, bytes): # Handle potential bytea data (like context?)
                      try:
                          return json.loads(data.decode('utf-8')) # Try decoding as JSON
                      except (UnicodeDecodeError, json.JSONDecodeError):
                          return data.hex() # Fallback to hex representation
                 else:
                    return data

            serialized_log = serialize_log_data(log_data)
            
            # Attempt to parse JSON strings within the steps (like context, prompt, response)
            for step in serialized_log.get('processing_steps', []):
                 for field in ['context', 'prompt', 'response', 'system_prompt', 'extracted_data']:
                     if isinstance(step.get(field), str):
                         try:
                             # Try parsing if it looks like JSON
                             if step[field].strip().startswith('{') or step[field].strip().startswith('['):
                                 step[field] = json.loads(step[field])
                         except json.JSONDecodeError:
                             pass # Keep as string if not valid JSON

            return jsonify(serialized_log), 200

    except Exception as e:
        log.error(f"Error fetching log details for log_id {log_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve log details"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@conversation_bp.route('/conversations/<uuid:conversation_id>/ai-control', methods=['GET', 'POST', 'OPTIONS'])
@require_api_key
def control_ai_responses(conversation_id):
    """
    Control AI responses for a conversation or user.
    
    Args:
        conversation_id: The ID of the conversation to control
        
    Request Body (for POST):
        action: 'stop' or 'resume'
        user_id: Optional user ID to control responses for all their conversations
        duration: Optional duration in hours for the stop (defaults to 24 hours)
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        if request.method == 'GET':
            # Return current status
            status = ai_control_service.get_stop_status(conversation_id)
            return jsonify({
                'success': True,
                'status': status
            })
        
        data = request.get_json()
        action = data.get('action')
        user_id = data.get('user_id')
        duration = data.get('duration')
        
        if action not in ['stop', 'resume']:
            return jsonify({
                'success': False,
                'error': 'Invalid action. Must be either "stop" or "resume"'
            }), 400
        
        if action == 'stop':
            # Convert duration to timedelta if provided
            duration_td = None
            if duration is not None:
                try:
                    duration_td = timedelta(hours=float(duration))
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'error': 'Invalid duration. Must be a number of hours.'
                    }), 400
            
            ai_control_service.stop_ai_responses(conversation_id, user_id, duration_td)
        else:
            ai_control_service.resume_ai_responses(conversation_id, user_id)
        
        # Get the current status
        status = ai_control_service.get_stop_status(conversation_id, user_id)
        
        return jsonify({
            'success': True,
            'message': f'AI responses {action}ed for {"user " + user_id if user_id else "conversation " + str(conversation_id)}',
            'status': status
        })
        
    except Exception as e:
        log.error(f"Error controlling AI responses: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def is_valid_uuid(val): # Added helper function
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False