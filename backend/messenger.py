from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import json
from functools import wraps

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
    # Your message processing logic here
    response = {
        'recipient': {'id': sender_id},
        'message': {'text': f"Received: {message}"}
    }
    return response

def send_message(recipient_id, response):
    """Send message to Facebook Messenger"""
    import requests
    
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
        return result.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def setup_messenger_routes(app):
    @app.route('/webhook', methods=['GET', 'POST'])
    @verify_fb_token
    def webhook():
        if request.method == 'POST':
            output = request.get_json()
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