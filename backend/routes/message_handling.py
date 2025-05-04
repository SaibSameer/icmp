# backend/routes/message_handling.py
from flask import jsonify, request, Blueprint, current_app, make_response
import uuid
import logging
import json
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection, get_db_pool
from openai_helper import call_openai
from backend.auth import require_internal_key, require_api_key
import re
import hmac # For signature verification
import hashlib # For signature verification
import requests # For calling internal APIs
from backend.message_processing.message_handler import MessageHandler
from backend.routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

bp = Blueprint('message_handling', __name__, url_prefix='/api')

# Attempt to import the main processing logic
try:
    from backend.message_processing.message_handler import MessageHandler
    # If MessageHandler uses the db pool directly, ensure it's initialized
    # from backend.db import initialize_db_pool, get_db_pool 
    # initialize_db_pool() # Ensure pool is initialized on app start
except ImportError:
    MessageHandler = None
    log.warning("MessageHandler class not found. Message processing logic is missing.")

def verify_facebook_signature(payload_body, signature_header):
    """Verify the request signature from Facebook."""
    if not signature_header:
        log.warning("Webhook signature header missing (X-Hub-Signature-256)")
        return False
    
    app_secret = current_app.config.get("FACEBOOK_APP_SECRET")
    if not app_secret:
        log.error("FACEBOOK_APP_SECRET not configured on the server.")
        return False # Cannot verify without the secret

    try:
        hash_method, signature_hash = signature_header.split('=', 1)
        if hash_method != 'sha256':
            log.warning(f"Unsupported webhook hash method: {hash_method}")
            return False
        
        expected_hash = hmac.new(
            app_secret.encode('utf-8'),
            payload_body, # Use the raw request body bytes
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_hash, signature_hash):
            log.warning("Webhook signature mismatch.")
            return False
        
        log.info("Webhook signature verified successfully.")
        return True
    except Exception as e:
        log.error(f"Error during webhook signature verification: {str(e)}", exc_info=True)
        return False

# Example endpoint for Facebook Messenger webhooks
@bp.route('/facebook', methods=['GET', 'POST'])
def facebook_webhook():
    # Handle verification challenge for Facebook
    if request.method == 'GET':
        verify_token = current_app.config.get("FACEBOOK_VERIFY_TOKEN", "DEFAULT_VERIFY_TOKEN") # Use a config var
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == verify_token:
            log.info('Facebook Webhook verification successful!')
            return challenge, 200
        else:
            log.warning('Facebook Webhook verification failed.')
            return 'Verification token mismatch', 403

    # Handle incoming messages
    if request.method == 'POST':
        # 1. Verify Signature (CRITICAL)
        signature = request.headers.get('X-Hub-Signature-256')
        raw_body = request.get_data() # Get raw bytes for signature check
        if not verify_facebook_signature(raw_body, signature):
             return jsonify({"status": "error", "message": "Signature verification failed"}), 403
        
        # 2. Parse Payload
        try:
            data = json.loads(raw_body.decode('utf-8')) # Parse body AFTER verification
        except json.JSONDecodeError:
             log.error("Failed to decode webhook JSON payload")
             return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
        
        log.info(f"Received Facebook webhook payload: {json.dumps(data)}")

        # 3. Process each message entry (Facebook sends batches)
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"] # Platform User ID
                        recipient_id = messaging_event["recipient"]["id"] # Your Page ID
                        message_text = messaging_event["message"].get("text")
                        # mid = messaging_event["message"].get("mid") # Message ID
                        
                        if message_text:
                            log.info(f"Processing message from {sender_id} to page {recipient_id}: '{message_text}'")
                            
                            # 4. Identify Business & Get Internal Key
                            conn = None
                            internal_key = None
                            business_id = None
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                # TODO: Update DB schema and query to map recipient_id (Page ID) to business_id
                                # Example assumes `facebook_page_id` column exists on `businesses` table:
                                cursor.execute("SELECT business_id, internal_api_key FROM businesses WHERE facebook_page_id = %s", (recipient_id,))
                                result = cursor.fetchone()
                                if result:
                                    business_id = str(result[0])
                                    internal_key = result[1]
                                    log.info(f"Mapped page {recipient_id} to business {business_id}")
                                else:
                                    log.error(f"Could not find business associated with Facebook Page ID: {recipient_id}")
                                    continue # Skip processing this message
                            except Exception as e:
                                log.error(f"DB error looking up business for page {recipient_id}: {str(e)}", exc_info=True)
                                continue # Skip processing this message
                            finally:
                                if conn:
                                    release_db_connection(conn)
                            
                            if not internal_key or not business_id:
                                continue # Skip if mapping failed

                            # 5. Process Message using MessageHandler (if available)
                            if MessageHandler:
                                try:
                                    # Assuming MessageHandler takes db_pool or connection factory
                                    # And internal_key if it needs to make authenticated internal API calls
                                    # message_handler = MessageHandler(get_db_pool(), internal_api_key=internal_key) 
                                    message_handler = MessageHandler(get_db_pool()) # Simpler assumption
                                    
                                    # Prepare data for the handler
                                    message_data = {
                                        'business_id': business_id,
                                        'user_id': sender_id, # Use platform sender ID as user ID
                                        'content': message_text,
                                        'platform': 'facebook' # Add platform info
                                        # Add conversation_id if available from context/lookup
                                    }
                                    
                                    processing_result = message_handler.process_message(message_data)
                                    
                                    # 6. Handle Result & Respond to Platform
                                    if processing_result.get('success'):
                                        response_to_user = processing_result.get('response', "Sorry, I couldn't process that.")
                                        log.info(f"Successfully processed message for business {business_id}. Response: '{response_to_user[:50]}...'")
                                        # TODO: Implement logic to send `response_to_user` back to Facebook `sender_id`
                                        # using Facebook Graph API (requires Page Access Token)
                                        # send_facebook_message(recipient_id, sender_id, response_to_user)
                                    else:
                                        log.error(f"MessageHandler failed for business {business_id}: {processing_result.get('error')}")
                                        # TODO: Optionally send an error message back to the user via Facebook API
                                        # send_facebook_message(recipient_id, sender_id, "Sorry, an error occurred.")

                                except Exception as proc_err:
                                    log.error(f"Error invoking MessageHandler for business {business_id}: {proc_err}", exc_info=True)
                                    # TODO: Optionally send an error message back to the user
                            else:
                                log.error("MessageHandler not loaded, cannot process message.")
                                # TODO: Optionally send error message back to user

        return "EVENT_RECEIVED", 200 # Acknowledge receipt to Facebook
    else:
        return jsonify({"error": "Method Not Allowed"}), 405

# Add similar endpoints for other platforms (WhatsApp, etc.) following the same pattern:
# 1. Signature Verification
# 2. Parse Payload
# 3. Identify Business & Get Internal Key (using platform-specific identifiers)
# 4. Call Internal Processing Logic (passing internal key for auth)

# register_message_routes seems unnecessary if using Blueprints directly in app.py
# def register_message_routes(app, require_api_key, limiter):
#     app.register_blueprint(bp)

@bp.route('/api/message', methods=['POST', 'OPTIONS'])
def handle_message():
    """Handle incoming messages."""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Extract and validate required fields
    business_id = data.get('business_id')
    user_id = data.get('user_id')
    content = data.get('content')
    conversation_id = data.get('conversation_id')

    if not all([business_id, user_id, content]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: business_id, user_id, content'
        }), 400

    if not is_valid_uuid(business_id) or not is_valid_uuid(user_id):
        return jsonify({
            'success': False,
            'error': 'Invalid UUID format for business_id or user_id'
        }), 400

    if conversation_id and not is_valid_uuid(conversation_id):
        return jsonify({
            'success': False,
            'error': 'Invalid UUID format for conversation_id'
        }), 400

    try:
        # Initialize message handler
        message_handler = MessageHandler(get_db_pool())
        
        # Process the message
        result = message_handler.process_message({
            'business_id': business_id,
            'user_id': user_id,
            'content': content,
            'conversation_id': conversation_id
        })

        if result.get('success'):
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        else:
            return jsonify(result), 500

    except Exception as e:
        log.error(f"Error processing message: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500