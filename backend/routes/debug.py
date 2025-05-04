from flask import Blueprint, jsonify, request, Response, stream_with_context
from backend.auth import require_api_key
import json
import time
from datetime import datetime

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/conversation/<conversation_id>', methods=['GET'])
@require_api_key
def get_conversation_debug(conversation_id):
    """
    Get debug information for a specific conversation.
    This includes all prompts, responses, and stage transitions.
    """
    try:
        # TODO: Implement actual database queries to get the debug information
        # This is example data for now
        debug_data = {
            "stages": [
                {
                    "id": "stage1",
                    "name": "Initial Greeting",
                    "confidence": 0.95,
                    "current": False
                },
                {
                    "id": "stage2",
                    "name": "Order Status",
                    "confidence": 0.88,
                    "current": True
                }
            ],
            "stageSelection": {
                "prompt": "Based on the user's message 'What's the status of my order?', determine the appropriate stage...",
                "response": "Stage: Order Status (confidence: 0.88)"
            },
            "dataExtraction": {
                "prompt": "Extract any order-related information from the message...",
                "response": "No specific order ID mentioned in the query."
            },
            "extractedData": {
                "intent": "order_status_query",
                "entities": {},
                "confidence": 0.88
            },
            "responseGeneration": {
                "prompt": "Generate a response asking the user for their order ID...",
                "response": "I'd be happy to help you check your order status. Could you please provide your order ID?"
            }
        }
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/message/<message_id>', methods=['GET'])
@require_api_key
def get_message_debug(message_id):
    """
    Get debug information for a specific message processing instance.
    """
    try:
        # TODO: Implement actual message debug info retrieval
        debug_data = {
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "processing_steps": [
                {
                    "step": "stage_selection",
                    "input": "What's the status of my order?",
                    "output": "Order Status stage selected",
                    "confidence": 0.88,
                    "processing_time": 0.45
                }
                # Add more steps as needed
            ]
        }
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/stages/<conversation_id>', methods=['GET'])
@require_api_key
def get_stage_navigation_debug(conversation_id):
    """
    Get stage navigation history for a conversation.
    """
    try:
        # TODO: Implement actual stage navigation history retrieval
        navigation_data = {
            "conversation_id": conversation_id,
            "stages": [
                {
                    "timestamp": "2024-04-08T10:00:00Z",
                    "from_stage": "Initial Greeting",
                    "to_stage": "Order Status",
                    "confidence": 0.88,
                    "trigger": "user_message"
                }
                # Add more stage transitions as needed
            ]
        }
        return jsonify(navigation_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/prompts/<message_id>', methods=['GET'])
@require_api_key
def get_prompt_generation_debug(message_id):
    """
    Get prompt generation details for a message.
    """
    try:
        # TODO: Implement actual prompt generation debug info retrieval
        prompt_data = {
            "message_id": message_id,
            "prompts": [
                {
                    "type": "stage_selection",
                    "template": "Based on the conversation history and available stages...",
                    "variables": {
                        "user_message": "What's the status of my order?",
                        "conversation_history": []
                    },
                    "final_prompt": "Complete prompt text here..."
                }
                # Add more prompts as needed
            ]
        }
        return jsonify(prompt_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/extraction/<message_id>', methods=['GET'])
@require_api_key
def get_data_extraction_debug(message_id):
    """
    Get data extraction results for a message.
    """
    try:
        # TODO: Implement actual data extraction debug info retrieval
        extraction_data = {
            "message_id": message_id,
            "extracted_data": {
                "intent": "order_status_query",
                "entities": {},
                "confidence": 0.88
            },
            "extraction_process": {
                "template_used": "data_extraction_template_1",
                "processing_time": 0.35,
                "confidence_scores": {
                    "intent": 0.88,
                    "entities": {}
                }
            }
        }
        return jsonify(extraction_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/events/<conversation_id>')
@require_api_key
def debug_events(conversation_id):
    """
    Stream debug events for a conversation using Server-Sent Events (SSE).
    """
    def generate():
        try:
            # TODO: Implement actual event streaming
            # This is just an example that sends a few events
            events = [
                {"timestamp": datetime.now().isoformat(), "message": "Processing started"},
                {"timestamp": datetime.now().isoformat(), "message": "Stage selection completed"},
                {"timestamp": datetime.now().isoformat(), "message": "Data extraction completed"},
                {"timestamp": datetime.now().isoformat(), "message": "Response generation completed"}
            ]
            
            for event in events:
                data = json.dumps(event)
                yield f"data: {data}\n\n"
                time.sleep(1)  # Simulate time between events
                
        except GeneratorExit:
            # Client disconnected
            pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )