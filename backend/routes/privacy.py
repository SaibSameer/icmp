import base64
import hashlib
import hmac
import json
import logging
import os
import uuid

from flask import Blueprint, request, jsonify, abort

from backend.db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

privacy_bp = Blueprint('privacy', __name__, url_prefix='/privacy')

# Load Facebook App Secret from environment variable
FB_APP_SECRET = os.getenv('FB_APP_SECRET')

def parse_signed_request(signed_request: str, secret: str) -> dict | None:
    \"\"\"Parses and verifies the Facebook signed_request.

    Args:
        signed_request: The signed_request string from Facebook.
        secret: The Facebook App Secret.

    Returns:
        The decoded payload dictionary if verification succeeds, otherwise None.
    \"\"\"
    if not signed_request or '.' not in signed_request:
        log.error(\"Invalid signed_request format.\")
        return None

    try:
        encoded_sig, payload = signed_request.split('.', 1)

        # Decode signature
        sig = base64.urlsafe_b64decode(encoded_sig + \"==\") # Add padding if needed

        # Decode data
        data = base64.urlsafe_b64decode(payload + \"==\") # Add padding if needed
        data = json.loads(data)

        if data.get('algorithm', '').upper() != 'HMAC-SHA256':
            log.error(f\"Unknown algorithm {data.get('algorithm')}\")
            return None

        # Check signature
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(expected_sig, sig):
            log.error(\"Invalid signature in signed_request.\")
            return None

        log.info(\"Signed request verified successfully.\")
        return data
    except (ValueError, TypeError, json.JSONDecodeError, binascii.Error) as e:
        log.error(f\"Error decoding/verifying signed_request: {e}\")
        return None
    except Exception as e:
        log.error(f\"Unexpected error parsing signed_request: {e}\", exc_info=True)
        return None


@privacy_bp.route('/facebook/delete', methods=['POST'])
def facebook_data_deletion():
    \"\"\"Handles Facebook's Data Deletion Request Callback.\"\"\"
    log.info(\"Received request on /privacy/facebook/delete\")

    if not FB_APP_SECRET:
        log.error(\"FB_APP_SECRET is not configured. Cannot process data deletion request.\")
        # Abort, but don't reveal internal config error to Facebook
        return jsonify({'error': 'Internal configuration error'}), 500

    signed_request_param = request.form.get('signed_request')
    if not signed_request_param:
        log.warning(\"Missing 'signed_request' parameter in Facebook data deletion request.\")
        return jsonify({'error': 'Missing signed_request parameter'}), 400

    log.info(f\"Received signed_request: {signed_request_param[:50]}...\") # Log prefix for safety

    payload = parse_signed_request(signed_request_param, FB_APP_SECRET)

    if payload is None:
        log.error(\"Failed to verify or parse signed_request.\")
        # According to FB docs, should still return 200 OK or 404 Not Found
        # Let's return 400 Bad Request as it failed verification
        return jsonify({'error': 'Invalid signed_request'}), 400

    fb_user_id = payload.get('user_id')
    if not fb_user_id:
        log.error(\"No user_id found in signed_request payload.\")
        return jsonify({'error': 'Missing user_id in payload'}), 400

    log.info(f\"Initiating data deletion process for Facebook User ID: {fb_user_id}\")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Data Deletion Logic ---
        # Find the user based on their Facebook ID (assuming stored in 'external_id')
        cursor.execute(\"SELECT user_id FROM users WHERE external_id = %s AND platform = 'facebook'\", (fb_user_id,))
        user_result = cursor.fetchone()

        if not user_result:
            log.warning(f\"User with Facebook ID {fb_user_id} not found in our system.\")
            # User not found - respond as if deletion is complete/not applicable
        else:
            internal_user_id = user_result[0]
            log.info(f\"Found internal user ID {internal_user_id} for Facebook ID {fb_user_id}. Proceeding with deletion.\")

            # Example: Delete related data first (adjust table/column names as needed)
            # cursor.execute(\"DELETE FROM messages WHERE user_id = %s\", (internal_user_id,))
            # cursor.execute(\"DELETE FROM conversations WHERE user_id = %s\", (internal_user_id,))
            # ... add other related data deletions here ...

            # Delete the user record itself
            cursor.execute(\"DELETE FROM users WHERE user_id = %s\", (internal_user_id,))

            conn.commit()
            log.info(f\"Successfully deleted data for Facebook User ID: {fb_user_id} (Internal ID: {internal_user_id})\")

        cursor.close()

    except Exception as e:
        if conn:
            conn.rollback() # Rollback on error
        log.error(f\"Database error during data deletion for Facebook User ID {fb_user_id}: {e}\", exc_info=True)
        # Respond with an error, but Facebook expects 200 OK or 404
        # We'll log the error but still return the success structure
        pass # Fall through to success response as per FB docs recommendations
    finally:
        if conn:
            release_db_connection(conn)

    # Respond to Facebook
    # Provide a URL to track status (can be your main site or a specific status page)
    # Generate a unique confirmation code
    status_url = f\"https://{request.host}/privacy/status\" # Example URL
    confirmation_code = f\"fbdel-{uuid.uuid4()}\"

    response_payload = {
        'url': status_url,
        'confirmation_code': confirmation_code
    }
    log.info(f\"Responding to Facebook data deletion request for User ID {fb_user_id} with code {confirmation_code}\")

    return jsonify(response_payload), 200

# You might want a simple status page (optional, can just be your main page)
@privacy_bp.route('/status', methods=['GET'])
def deletion_status():
    \"\"\"A simple page users can be directed to after requesting deletion.\"\"\"
    # You could enhance this to show status based on confirmation_code if needed
    return \"Your data deletion request is being processed. Please allow up to 48 hours.\", 200 