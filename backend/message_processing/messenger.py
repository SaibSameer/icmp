from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import json
import uuid
import logging
from functools import wraps
from backend.database.db import get_db_connection, release_db_connection, get_db_pool

# Set up logging
log = logging.getLogger(__name__)

# Facebook Messenger verification token
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')

def verify_fb_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'GET':
            token_sent = request.args.get('hub.verify_token')
            if token_sent == VERIFY_TOKEN:
                return request.args.get('hub.challenge')
            return 'Invalid verification token'
        return f(*args, **kwargs)
    return decorated_function

def handle_message(sender_id, message):
    """Handle incoming messages from Facebook Messenger"""
    log.info(f"Received message from {sender_id}: {message}")
    
    # Get a database connection
    conn = get_db_connection()
    try:
        # Check if this user exists in our system
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE external_id = %s", (sender_id,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
        else:
            # Create a new user if they don't exist
            user_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (user_id, external_id, first_name, last_name) VALUES (%s, %s, %s, %s)",
                (user_id, sender_id, "Facebook", "User")
            )
            conn.commit()
        
        # Get the business ID (using a default for now)
        cursor.execute("SELECT business_id FROM businesses LIMIT 1")
        business_result = cursor.fetchone()
        
        if not business_result:
            log.error("No business found in the database")
            return {
                'recipient': {'id': sender_id},
                'message': {'text': "Sorry, there was an error processing your message."}
            }
        
        business_id = business_result[0]
        
        # Process the message using the message handler
        from backend.message_processing.message_handler import MessageHandler
        
        message_handler = MessageHandler(get_db_pool())
        result = message_handler.process_message({
            'business_id': business_id,
            'user_id': user_id,
            'content': message,
            'source': 'facebook_messenger'
        })
        
        if result.get('success'):
            response_text = result.get('response', '')
        else:
            response_text = "Sorry, there was an error processing your message."
            log.error(f"Error processing message: {result.get('error')}")
        
        return {
            'recipient': {'id': sender_id},
            'message': {'text': response_text}
        }
    except Exception as e:
        log.error(f"Error handling message: {str(e)}", exc_info=True)
        return {
            'recipient': {'id': sender_id},
            'message': {'text': "Sorry, there was an error processing your message."}
        }
    finally:
        release_db_connection(conn)

def send_message(recipient_id, response):
    """Send message to Facebook Messenger"""
    import requests
    
    if not PAGE_ACCESS_TOKEN:
        log.error("Facebook PAGE_ACCESS_TOKEN is not set")
        return None
    
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps(response)
    
    url = "https://graph.facebook.com/v18.0/me/messages"
    
    try:
        result = requests.post(url, params=params, headers=headers, data=data)
        log.info(f"Facebook API response: {result.status_code} - {result.text}")
        return result.json()
    except Exception as e:
        log.error(f"Error sending message: {e}", exc_info=True)
        return None

def setup_messenger_routes(app):
    @app.route('/webhook', methods=['GET', 'POST'])
    @verify_fb_token
    def webhook():
        if request.method == 'POST':
            output = request.get_json()
            log.info(f"Received webhook data: {json.dumps(output)}")
            
            for event in output['entry']:
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'):
                        sender_id = message['sender']['id']
                        if message['message'].get('text'):
                            message_text = message['message']['text']
                            response = handle_message(sender_id, message_text)
                            send_message(sender_id, response)
        return "Message Processed"