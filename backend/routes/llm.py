from flask import Blueprint, jsonify, request, current_app, g
import logging
import json
import uuid
from datetime import datetime
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_internal_key
from backend.openai_helper import call_openai

log = logging.getLogger(__name__)

# Create a blueprint for LLM routes
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@llm_bp.route('/generate', methods=['POST', 'OPTIONS'])
@require_internal_key
def generate_llm_response():
    """Generate a response using the call_openai function."""
    if request.method == 'OPTIONS':
        return jsonify(success=True), 200
    
    if not hasattr(g, 'business_id'):
        log.error("Business context missing in generate_llm_response")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), 400

    input_text = data.get('input_text')
    system_prompt = data.get('system_prompt', '') # System prompt might not be directly used by call_openai
    conversation_id = data.get('conversation_id') # Not used by call_openai
    agent_id = data.get('agent_id') # Not used by call_openai
    call_type = data.get('call_type', 'general') # Not used by call_openai
    
    if not input_text:
        log.error(f"Missing input_text for business {business_id}")
        return jsonify({'success': False, 'error': 'Missing input_text parameter'}), 400
    
    log.info(f"Generating LLM response via call_openai for business {business_id}")
    # Prepare the prompt for call_openai. 
    # NOTE: call_openai in helper only takes a single prompt string.
    # We might need a more sophisticated helper or combine prompts here.
    # For now, just pass input_text. System prompt is ignored by call_openai.
    final_prompt = input_text 
    if system_prompt: 
        log.warning(f"System prompt provided but call_openai might not use it directly. Prompt: {system_prompt}")
        # How should system prompt be integrated? Prepend? Pass differently?
        # Example: final_prompt = f"{system_prompt}\n\nUser: {input_text}"

    # Generate a unique ID for logging/reference, though call_openai doesn't take it
    llm_call_id = str(uuid.uuid4())
    log.info(f"Generated LLM call ID: {llm_call_id}")

    try:
        # Call the actual function from the helper
        response_text = call_openai(final_prompt)
        
        # Check if response indicates an error (based on mock response structure)
        if "mock response" in response_text and ("API key not configured" in response_text or "API key format is invalid" in response_text or "call failed" in response_text):
             log.error(f"call_openai failed for business {business_id}: {response_text}")
             # Return a generic error, don't expose internal details like mock response structure
             return jsonify({'success': False, 'error': 'LLM call failed due to configuration or API error.'}), 500

        return jsonify({
            'success': True,
            'call_id': llm_call_id, # Return the generated ID
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        log.error(f"Error calling call_openai for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/calls/recent', methods=['GET', 'OPTIONS'])
@require_internal_key
def get_recent_llm_calls():
    """Get recent LLM calls for the authenticated business."""
    if request.method == 'OPTIONS':
        return jsonify(success=True), 200
    
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    
    limit = int(request.args.get('limit', 10))
    log.info(f"Fetching recent {limit} LLM calls for business {business_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check table existence (optional but good practice)
        cursor.execute("SELECT to_regclass('public.llm_calls')")
        if cursor.fetchone()[0] is None:
            log.warning(f"llm_calls table not found for business {business_id}")
            return jsonify([])
        
        # Fetch recent calls using business_id from context
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
        columns = [desc[0] for desc in cursor.description] 
        for row in cursor.fetchall():
            call_data = dict(zip(columns, row))
            # Format dates and UUIDs
            call_data['call_id'] = str(call_data['call_id'])
            call_data['business_id'] = str(call_data['business_id'])
            call_data['timestamp'] = call_data['timestamp'].isoformat() if call_data['timestamp'] else None
            calls.append(call_data)
        
        return jsonify(calls)
        
    except Exception as e:
        log.error(f"Database error fetching recent calls for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@llm_bp.route('/calls/<call_id>', methods=['GET', 'OPTIONS'])
@require_internal_key
def get_llm_call_details(call_id):
    """Get details of a specific LLM call, ensuring it belongs to the authenticated business."""
    if request.method == 'OPTIONS':
        return jsonify(success=True), 200
    
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Fetching details for LLM call {call_id} for business {business_id}")

    # Validate call_id format (optional but recommended)
    try:
        uuid.UUID(call_id)
    except ValueError:
         return jsonify({'success': False, 'error': 'Invalid call_id format'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check table existence
        cursor.execute("SELECT to_regclass('public.llm_calls')")
        if cursor.fetchone()[0] is None:
             log.warning(f"llm_calls table not found when fetching details for call {call_id}")
             return jsonify({'success': False, 'error': 'LLM call data not available'}), 404
        
        # Fetch call details, ensuring it matches the business_id from context
        cursor.execute(
            """
            SELECT call_id, business_id, input_text, response, system_prompt, call_type, timestamp, 
                   agent_id, conversation_id, cost, duration, status, error_message
            FROM llm_calls
            WHERE call_id = %s AND business_id = %s;
            """, (call_id, business_id)
        )
        
        result = cursor.fetchone()
        if not result:
            log.warning(f"LLM Call {call_id} not found or not authorized for business {business_id}")
            return jsonify({'success': False, 'error': 'LLM call not found or access denied'}), 404
            
        columns = [desc[0] for desc in cursor.description]
        call_details = dict(zip(columns, result))
        
        # Format dates and UUIDs
        for key in ['call_id', 'business_id', 'agent_id', 'conversation_id']:
            if call_details.get(key):
                 call_details[key] = str(call_details[key])
        if call_details.get('timestamp'):
            call_details['timestamp'] = call_details['timestamp'].isoformat()
            
        return jsonify(call_details)
        
    except Exception as e:
        log.error(f"Database error fetching details for call {call_id}, business {business_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@llm_bp.route('/call', methods=['POST'])
@require_internal_key
def handle_llm_call():
    """Handle an LLM call request using call_openai."""
    if not hasattr(g, 'business_id'):
        log.error("Business context missing in handle_llm_call")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    
    data = request.get_json()
    if not data:
         return jsonify({'success': False, 'error': 'Request must be JSON'}), 400

    input_text = data.get('prompt') # Use 'prompt' key from request
    system_prompt = data.get('system_prompt') # Not used by call_openai
    # Other params like conversation_id, agent_id, call_type are ignored by call_openai

    if not input_text:
        log.warning(f"Missing prompt for /call endpoint, business {business_id}")
        return jsonify({'success': False, 'error': 'Missing prompt parameter'}), 400

    log.info(f"Handling /call request via call_openai for business {business_id}")
    final_prompt = input_text # See note in /generate route about system prompt
    if system_prompt:
        log.warning(f"System prompt provided to /call but call_openai might not use it. Prompt: {system_prompt}")

    llm_call_id = str(uuid.uuid4())
    log.info(f"Generated LLM call ID for /call: {llm_call_id}")

    try:
        # Call the actual helper function
        response_text = call_openai(final_prompt)

        # Check for mock error response
        if "mock response" in response_text and ("API key not configured" in response_text or "API key format is invalid" in response_text or "call failed" in response_text):
             log.error(f"call_openai failed via /call for business {business_id}: {response_text}")
             return jsonify({'success': False, 'error': 'LLM call failed due to configuration or API error.'}), 500
        
        return jsonify({
            'success': True,
            'call_id': llm_call_id,
            'response': response_text
        })

    except Exception as e:
        log.error(f"Error in /call endpoint for business {business_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500