"""
Message Simulator Routes

This module provides API endpoints for simulating message processing and testing
the template system.
"""

from flask import Blueprint, request, jsonify
from ..message_processing.message_simulator import MessageSimulator
from ..auth import require_api_key, require_auth

bp = Blueprint('message_simulator', __name__)
simulator = MessageSimulator()

@bp.route('/message', methods=['POST', 'OPTIONS'])
@require_api_key
@require_auth
def simulate_message():
    """
    Endpoint to simulate sending a message.
    
    Required Headers:
    - businessapikey: Your business API key
    - Authorization: Bearer token for authentication
    
    Expected JSON body:
    {
        "user_id": "string",
        "business_id": "string",
        "message_content": "string",
        "conversation_id": "string" (optional)
    }
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'business_id', 'message_content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f"Missing required field: {field}"
                }), 400
        
        # Simulate the message
        result = simulator.simulate_message(
            user_id=data['user_id'],
            message_content=data['message_content'],
            business_id=data['business_id'],
            conversation_id=data.get('conversation_id')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/conversation/<conversation_id>', methods=['GET'])
@require_api_key
@require_auth
def get_conversation_history(conversation_id):
    """
    Get the history of a specific conversation.
    
    Required Headers:
    - businessapikey: Your business API key
    - Authorization: Bearer token for authentication
    """
    try:
        history = simulator.get_conversation_history(conversation_id)
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'messages': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/user/<user_id>/conversations', methods=['GET'])
@require_api_key
@require_auth
def get_user_conversations(user_id):
    """
    Get all conversations for a specific user.
    
    Required Headers:
    - businessapikey: Your business API key
    - Authorization: Bearer token for authentication
    """
    try:
        conversations = simulator.get_user_conversations(user_id)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 