#!/usr/bin/env python
# app.py - Main Flask application entry point

import sys
import os
import secrets
import logging
from flask import Flask, jsonify, request, Response, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import json
import uuid

# Ensure the backend directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import modules from our app
from auth import require_api_key
from db import get_db_connection, release_db_connection, execute_query, CONNECTION_POOL
from config import Config

# Routes imports
from routes.message_handling import bp as message_bp
from routes.routing import bp as routing_bp
from routes.templates import templates_bp
from routes.stages import stages_bp
from routes.template_management import template_management_bp
from routes.conversation_management import conversation_bp
from routes.businesses import bp as businesses_bp
from routes.auth_bp import bp as auth_bp
from routes.configuration import bp as config_bp
from routes.agents import agents_bp
from routes.users import users_bp
from routes.template_variables import template_variables_bp
from routes.llm import llm_bp

# Import here to avoid circular imports
from create_default_stage import create_default_stage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
    ]
)
log = logging.getLogger(__name__)
log.info("--- Logging configured (basicConfig) ---")

# Function to create and initialize the default stage
def initialize_default_stage():
    """Create default stage if one doesn't exist."""
    try:
        log.info("Creating default stage if needed...")
        default_stage_id = create_default_stage()
        log.info(f"Default stage ID: {default_stage_id}")
        return default_stage_id
    except Exception as e:
        log.error(f"Error creating default stage: {str(e)}", exc_info=True)
        return None

# Create the Flask app
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    CORS(app, 
         supports_credentials=True,
         resources={
             r"/*": {
                 "origins": [
                     "http://localhost:3000", 
                     "http://127.0.0.1:3000",
                     "http://localhost:8000", 
                     "http://127.0.0.1:8000",
                     "http://192.168.0.105:8000",
                     "null",
                     "file://"  # Allow requests from file:// protocol
                 ],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "businessapikey", "Accept", "Origin"],
                 "expose_headers": ["Content-Type", "Authorization", "businessapikey"],
                 "supports_credentials": True,
                 "max_age": 3600  # Cache preflight requests for 1 hour
             }
         })
    
    # Configure schema validation
    app.config['SCHEMAS'] = {}
    
    # Configure API key
    app.config['ICMP_API_KEY'] = Config.ICMP_API_KEY
    log.info(f"ICMP_API_KEY loaded: {app.config['ICMP_API_KEY']}")
    
    # Configure limiter
    limiter = Limiter(
        lambda: get_remote_address(),
        app=app,
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )
    
    # Disable limiter in certain environments
    if os.environ.get('DISABLE_RATE_LIMITS') or app.config.get('TESTING'):
        limiter.enabled = False
    
    # --- Request Logging ---
    log.info("--- Registering @app.before_request hook ---")
    @app.before_request
    def log_request_info():
        """Log basic info about each request."""
        log.info("!!! Request received: %s %s from %s !!!", 
                  request.method, request.path, request.remote_addr)
        # Log more detailed info at DEBUG level
        log.info({
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr
        })
        
    log.info("--- Registering @app.after_request hook ---")
    @app.after_request
    def log_response_info(response):
        """Log info about the response to each request."""
        log.info("!!! Request finished: %s, Status: %s !!!", 
                  request.path, response.status_code)
        return response
    
    # --- Route Handlers ---
    @app.route('/')
    def home():
        """Home route."""
        return jsonify({
            "message": "ICMP Events API is running",
            "version": "1.0.0",
            "status": "ok"
        })
    
    @app.route('/ping')
    def ping():
        """Health check route."""
        log.info("--- Inside /ping route handler ---")
        return jsonify({
            "response": "pong",
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/health', methods=['GET'])
    def health():
        """Health check route with more detailed status."""
        conn = None
        try:
            conn = get_db_connection()
            is_db_connected = conn is not None
            
            return jsonify({
                "status": "healthy",
                "date": datetime.now().isoformat(),
                "database": "connected" if is_db_connected else "disconnected",
                "schemas_loaded": app.config.get('SCHEMAS') is not None
            })
        except Exception as e:
            log.error(f"Health check error: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "date": datetime.now().isoformat(),
                "database": "error",
                "error": str(e)
            }), 500
        finally:
            if conn:
                release_db_connection(conn)

    @app.route('/api/save-config', methods=['POST', 'OPTIONS'])
    def save_config():
        if request.method == 'OPTIONS':
            return '', 204  # Return a 204 No Content response for preflight requests
        
        try:
            data = request.get_json()
            log.info(f"Received data: {data}")
            
            # Validate required fields
            required_fields = ['userId', 'businessId', 'businessApiKey']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                log.error(f"Missing required fields: {missing_fields}")
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }), 400
            
            # Extract fields and trim whitespace
            user_id = data.get('userId', '').strip()
            business_id = data.get('businessId', '').strip()
            business_api_key = data.get('businessApiKey', '').strip()
            
            # Validate fields
            if not all([user_id, business_id, business_api_key]):
                log.error("Empty or invalid fields")
                return jsonify({
                    'error': 'Empty or invalid fields',
                    'details': {
                        'userId': bool(user_id),
                        'businessId': bool(business_id),
                        'businessApiKey': bool(business_api_key)
                    }
                }), 400
            
            # Save to database
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE user_id = %s;
                    """, (user_id,)
                )
                user_exists = cursor.fetchone() is not None
                
                if not user_exists:
                    # Create a minimal user record if it doesn't exist
                    cursor.execute(
                        """
                        INSERT INTO users (user_id, first_name, last_name, email)
                        VALUES (%s, %s, %s, %s);
                        """, (user_id, 'User', 'User', f"{user_id}@example.com")
                    )
                
                # Check if business exists
                cursor.execute(
                    """
                    SELECT business_id
                    FROM businesses
                    WHERE business_id = %s;
                    """, (business_id,)
                )
                business_exists = cursor.fetchone() is not None
                
                if not business_exists:
                    # Create a new business with the user as owner
                    cursor.execute(
                        """
                        INSERT INTO businesses (business_id, api_key, owner_id, business_name)
                        VALUES (%s, %s, %s, %s);
                        """, (business_id, business_api_key, user_id, f"Business {business_id[:8]}")
                    )
                else:
                    # Update the business's API key and owner_id
                    cursor.execute(
                        """
                        UPDATE businesses
                        SET api_key = %s, owner_id = %s
                        WHERE business_id = %s;
                        """, (business_api_key, user_id, business_id)
                    )
                
                conn.commit()
                log.info(f"Successfully saved configuration for user {user_id} and business {business_id}")
                
                # Set the businessApiKey cookie
                response = jsonify({
                    'message': 'Configuration saved successfully',
                    'user_id': user_id,
                    'business_id': business_id,
                    'success': True
                })
                
                # Set the cookie with HttpOnly flag for security
                response.set_cookie(
                    'businessApiKey',
                    business_api_key,
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax',
                    max_age=86400  # 24 hours
                )
                
                return response
                
            except Exception as e:
                conn.rollback()
                log.error(f"Database error: {str(e)}")
                return jsonify({
                    'error': 'Database error',
                    'details': str(e)
                }), 500
            finally:
                if conn:
                    release_db_connection(conn)
            
        except Exception as e:
            log.error(f"Error processing request: {str(e)}")
            return jsonify({
                'error': 'Invalid request',
                'details': str(e)
            }), 400

    @app.route('/api/lookup-owner', methods=['POST', 'OPTIONS'])
    def lookup_owner():
        """Look up the owner ID for a business."""
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
        
        # Extract values first
        business_id_raw = data.get('businessId')
        business_api_key_raw = data.get('businessApiKey')
        
        # Convert to string and strip only if the values exist
        business_id = business_id_raw.strip() if isinstance(business_id_raw, str) else business_id_raw
        business_api_key = business_api_key_raw.strip() if isinstance(business_api_key_raw, str) else business_api_key_raw

        # Check for missing parameters
        if not all([business_id, business_api_key]):
            logging.error("Missing parameters in lookup_owner")
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400

        # Verify credentials and lookup owner
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Validate business credentials and get owner ID
            cursor.execute(
                """
                SELECT owner_id
                FROM businesses
                WHERE business_id = %s AND api_key = %s;
                """, (business_id, business_api_key)
            )
            result = cursor.fetchone()

            if not result:
                logging.error(f"Invalid business credentials in lookup_owner: business_id={business_id}")
                return jsonify({'success': False, 'error': 'Invalid business credentials'}), 401

            owner_id = result[0]
            response = jsonify({
                'success': True,
                'owner_id': owner_id,
                'business_id': business_id
            })
            
            # Set CORS headers on the response
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            return response

        except Exception as e:
            logging.error(f"Error in lookup_owner: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            if conn:
                release_db_connection(conn)

    @app.route('/api/verify-owner', methods=['POST', 'OPTIONS'])
    def verify_owner():
        """Verify if a user is the owner of a business."""
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            # When allowing credentials, we can't use wildcard origin
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract values first
        user_id_raw = data.get('userId')
        business_id_raw = data.get('businessId')
        business_api_key_raw = data.get('businessApiKey')
        
        # Convert to string and strip only if the values exist
        user_id = user_id_raw.strip() if isinstance(user_id_raw, str) else user_id_raw
        business_id = business_id_raw.strip() if isinstance(business_id_raw, str) else business_id_raw
        business_api_key = business_api_key_raw.strip() if isinstance(business_api_key_raw, str) else business_api_key_raw

        # Check for missing parameters
        if not all([user_id, business_id, business_api_key]):
            logging.error("Missing parameters in verify_owner")
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400

        # Check for invalid types
        if not all(isinstance(value, str) for value in [user_id, business_id, business_api_key]):
            logging.error("Invalid parameter types in verify_owner")
            return jsonify({'success': False, 'error': 'Invalid parameter types'}), 400

        # Verify owner status
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Validate business credentials and check if user is the owner
            cursor.execute(
                """
                SELECT 1
                FROM businesses
                WHERE business_id = %s AND api_key = %s AND owner_id = %s;
                """, (business_id, business_api_key, user_id)
            )
            is_owner = cursor.fetchone() is not None

            if not is_owner:
                # Check if credentials are valid but user is not the owner
                cursor.execute(
                    """
                    SELECT 1
                    FROM businesses
                    WHERE business_id = %s AND api_key = %s;
                    """, (business_id, business_api_key)
                )
                valid_credentials = cursor.fetchone() is not None
                
                if valid_credentials:
                    logging.error(f"User {user_id} attempted to access owner features but is not the owner of business {business_id}")
                    return jsonify({'success': False, 'error': 'Access denied: Not the business owner'}), 403
                else:
                    logging.error(f"Invalid business credentials in verify_owner: business_id={business_id}")
                    return jsonify({'success': False, 'error': 'Invalid business credentials'}), 401

            response = jsonify({'success': True})
            # Set CORS headers on the response
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            # Set cookies with proper security attributes
            # Use secure=False for HTTP development
            response.set_cookie(
                'businessApiKey',
                str(business_api_key),
                httponly=True,
                secure=False,  # Set to False for HTTP development
                samesite='Lax',  # Changed to Lax for better compatibility
                max_age=3600  # 1 hour expiry
            )

            return response

        except Exception as e:
            logging.error(f"Error in verify_owner: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            if conn:
                release_db_connection(conn)

    # Register blueprints
    app.register_blueprint(message_bp, url_prefix='/api')
    app.register_blueprint(routing_bp)
    
    # Log registration of templates blueprints to help debug route conflicts
    log.info("Registering templates_bp at /templates")
    app.register_blueprint(templates_bp, url_prefix='/templates')
    
    log.info("Registering template_management_bp at /api/templates")
    # POTENTIAL CONFLICT: Both templates_bp and template_management_bp handle templates
    # templates_bp uses /templates, while template_management_bp uses /api/templates
    # Make sure frontend calls the correct endpoint for default templates (/api/templates/default-templates)
    app.register_blueprint(template_management_bp, url_prefix='/api/templates')
    
    app.register_blueprint(stages_bp, url_prefix='/stages')
    app.register_blueprint(conversation_bp, url_prefix='/conversations')
    app.register_blueprint(businesses_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(config_bp, url_prefix='/config')
    app.register_blueprint(agents_bp)
    app.register_blueprint(users_bp)
    
    # Register the template variables blueprint
    log.info("Registering template_variables_bp at /api/variables")
    app.register_blueprint(template_variables_bp, url_prefix='/api/variables')
    
    # Register the LLM blueprint
    log.info("Registering llm_bp at /api/llm")
    app.register_blueprint(llm_bp, url_prefix='/api/llm')
    
    # Initialize the default stage
    with app.app_context():
        initialize_default_stage()
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', debug=True)