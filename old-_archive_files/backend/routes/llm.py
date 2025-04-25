from flask import Blueprint, jsonify, request, current_app
import logging
import json
import uuid
from datetime import datetime
from auth import require_business_api_key
from db import get_db_connection, release_db_connection
from ai.llm_service import LLMService

log = logging.getLogger(__name__)

# Create a blueprint for LLM routes
llm_bp = Blueprint('llm', __name__)

# Initialize LLM service
llm_service = LLMService()

@llm_bp.route('/generate', methods=['POST', 'OPTIONS'])
@require_business_api_key
def generate_llm_response():
    """Generate a response using the LLM service."""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Get parameters from request
    data = request.get_json()
    business_id = data.get('business_id')
    input_text = data.get('input_text')
    system_prompt = data.get('system_prompt', '')
    conversation_id = data.get('conversation_id')
    agent_id = data.get('agent_id')
    llm_call_id = data.get('llm_call_id')  # Get llm_call_id if provided
    call_type = data.get('call_type', 'general')
    
    # Check for missing parameters
    if not all([business_id, input_text]):
        log.error("Missing parameters in generate_llm_response")
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
    
    try:
        # Generate response using LLM service
        response_text = llm_service.generate_response(
            input_text=input_text,
            system_prompt=system_prompt,
            conversation_id=conversation_id,
            agent_id=agent_id,
            call_type=call_type,
            business_id=business_id,
            llm_call_id=llm_call_id  # Pass llm_call_id if provided
        )
        
        # Get the call_id from the response
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get the most recent call for this business
            cursor.execute(
                """
                SELECT call_id, timestamp
                FROM llm_calls
                WHERE business_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
                """, (business_id,)
            )
            
            result = cursor.fetchone()
            if result:
                call_id = result[0]
                timestamp = result[1]
            else:
                # Fallback to generating a new call_id if none found
                call_id = str(uuid.uuid4())
                timestamp = datetime.now()
            
            return jsonify({
                'success': True,
                'call_id': call_id,
                'response': response_text,
                'timestamp': timestamp.isoformat() if timestamp else datetime.now().isoformat()
            })
            
        except Exception as e:
            log.error(f"Database error in generate_llm_response: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            if conn:
                release_db_connection(conn)
                
    except Exception as e:
        log.error(f"Error generating LLM response: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/calls/recent', methods=['GET', 'OPTIONS'])
@require_business_api_key
def get_recent_llm_calls():
    """Get recent LLM calls for a business."""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response
    
    # Get parameters
    business_id = request.args.get('business_id')
    limit = int(request.args.get('limit', 10))
    
    # Check for missing parameters
    if not business_id:
        log.error("Missing business_id parameter in get_recent_llm_calls")
        return jsonify({'success': False, 'error': 'Missing business_id parameter'}), 400
    
    # Get recent calls from the database
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if the llm_calls table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'llm_calls'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Return empty list if table doesn't exist
            return jsonify([])
        
        # Get recent calls
        cursor.execute(
            """
            SELECT call_id, business_id, input_text, response, system_prompt, call_type, timestamp
            FROM llm_calls
            WHERE business_id = %s
            ORDER BY timestamp DESC
            LIMIT %s;
            """, (business_id, limit)
        )
        
        calls = []
        for row in cursor.fetchall():
            calls.append({
                'call_id': row[0],
                'business_id': row[1],
                'input_text': row[2],
                'response': row[3],
                'system_prompt': row[4],
                'call_type': row[5],
                'timestamp': row[6].isoformat() if row[6] else None
            })
        
        return jsonify(calls)
        
    except Exception as e:
        log.error(f"Database error in get_recent_llm_calls: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@llm_bp.route('/calls/<call_id>', methods=['GET', 'OPTIONS'])
@require_business_api_key
def get_llm_call_details(call_id):
    """Get details of a specific LLM call."""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response
    
    # Get parameters
    business_id = request.args.get('business_id')
    
    # Check for missing parameters
    if not business_id:
        log.error("Missing business_id parameter in get_llm_call_details")
        return jsonify({'success': False, 'error': 'Missing business_id parameter'}), 400
    
    # Get call details from the database
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if the llm_calls table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'llm_calls'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return jsonify({'success': False, 'error': 'LLM calls table does not exist'}), 404
        
        # Get call details
        cursor.execute(
            """
            SELECT call_id, business_id, input_text, response, system_prompt, call_type, timestamp
            FROM llm_calls
            WHERE call_id = %s AND business_id = %s;
            """, (call_id, business_id)
        )
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Call not found'}), 404
        
        call_details = {
            'call_id': row[0],
            'business_id': row[1],
            'input_text': row[2],
            'response': row[3],
            'system_prompt': row[4],
            'call_type': row[5],
            'timestamp': row[6].isoformat() if row[6] else None
        }
        
        return jsonify(call_details)
        
    except Exception as e:
        log.error(f"Database error in get_llm_call_details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)