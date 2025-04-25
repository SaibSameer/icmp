from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import json
import requests
from functools import wraps

# WhatsApp API credentials
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

def verify_whatsapp_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'GET':
            token_sent = request.args.get('hub.verify_token')
            if token_sent == WHATSAPP_VERIFY_TOKEN:
                return request.args.get('hub.challenge')
            return 'Invalid verification token'
        return f(*args, **kwargs)
    return decorated_function

def handle_whatsapp_message(sender_id, message):
    """Handle incoming messages from WhatsApp"""
    # Your message processing logic here
    response = {
        'messaging_product': 'whatsapp',
        'to': sender_id,
        'type': 'text',
        'text': {'body': f"Received: {message}"}
    }
    return response

def send_whatsapp_message(recipient_id, response):
    """Send message to WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        result = requests.post(url, headers=headers, json=response)
        return result.json()
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return None

def setup_whatsapp_routes(app):
    @app.route('/whatsapp-webhook', methods=['GET', 'POST'])
    @verify_whatsapp_token
    def whatsapp_webhook():
        if request.method == 'POST':
            output = request.get_json()
            
            # Handle WhatsApp message
            if 'entry' in output:
                for entry in output['entry']:
                    for change in entry.get('changes', []):
                        if 'value' in change:
                            value = change['value']
                            if 'messages' in value:
                                for message in value['messages']:
                                    if message['type'] == 'text':
                                        sender_id = message['from']
                                        message_text = message['text']['body']
                                        response = handle_whatsapp_message(sender_id, message_text)
                                        send_whatsapp_message(sender_id, response)
            
            return jsonify({'status': 'success'})
        
        return "WhatsApp Webhook Setup" 