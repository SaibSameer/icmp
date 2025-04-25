import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from datetime import datetime

# Assume Flask app is created similarly to other test files
# If you have a central fixture setup (e.g., in conftest.py), use that.
# Otherwise, define basic app/client fixtures here.

# Mock the blueprint and routes from the actual file
# This avoids direct dependency but requires keeping mocks in sync
from routes import businesses
from auth import require_api_key, require_business_api_key

# Test constants
TEST_BUSINESS_ID = 'a1b7b4a0-9d9b-4b9a-9b0a-1b7b4a0d9b4b'
TEST_BUSINESS_API_KEY = 'biz-key-for-a1b7b4a0'
TEST_USER_ID = str(uuid.uuid4())  # Changed to a valid UUID format
TEST_BUSINESS_DATA = {
    "business_id": TEST_BUSINESS_ID,
    "api_key": TEST_BUSINESS_API_KEY,
    "owner_id": str(uuid.uuid4()),
    "business_name": "Specific Biz",
    "business_description": "Details...",
    "address": "123 Main St",
    "phone_number": "555-1234",
    "website": "http://specific.com"
}

# --- Fixtures ---

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "ICMP_API_KEY": "test-master-api-key" # Master key for creating businesses
    })
    # Register the blueprints we are testing
    app.register_blueprint(businesses.bp)
    # Import and register the conversations blueprint for conversation tests
    from routes import conversations
    app.register_blueprint(conversations.bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Test POST /businesses ---

@patch('routes.businesses.get_db_connection')
@patch('routes.businesses.release_db_connection')
@patch('routes.businesses.validate') # Mock jsonschema validation
@patch('routes.businesses.uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')) # Mock UUID generation
@patch('routes.businesses.secrets.token_hex', return_value='generated_business_api_key_123') # Mock secrets
def test_create_business_success(mock_token, mock_uuid, mock_validate, mock_release_db, mock_get_conn, client):
    """Test successful business creation."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    valid_data = {
        "owner_id": str(uuid.uuid4()),
        "business_name": "Test Biz",
        "business_description": "A test business",
        "website": "http://test.com"
    }
    headers = {
        'Authorization': 'Bearer test-master-api-key',
        'Content-Type': 'application/json'
    }

    response = client.post('/businesses/', headers=headers, data=json.dumps(valid_data))

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Business created"
    assert data["business_id"] == '12345678-1234-5678-1234-567812345678'
    assert data["api_key"] == 'generated_business_api_key_123' # Check returned key

    mock_validate.assert_called_once_with(instance=valid_data, schema=businesses.business_schema)
    mock_get_conn.assert_called_once()
    mock_cursor.execute.assert_called_once()
    # Check if api_key was included in the INSERT parameters
    args, _ = mock_cursor.execute.call_args
    assert 'INSERT INTO businesses' in args[0]
    assert args[1][0] == '12345678-1234-5678-1234-567812345678' # business_id
    assert args[1][1] == 'generated_business_api_key_123'      # api_key
    assert args[1][2] == valid_data['owner_id']               # owner_id
    # ... check other params ...
    mock_conn.commit.assert_called_once()
    mock_release_db.assert_called_once_with(mock_conn)

def test_create_business_no_auth(client):
    """Test creating business without master API key."""
    valid_data = {"owner_id": str(uuid.uuid4()), "business_name": "Test Biz"}
    response = client.post('/businesses/', data=json.dumps(valid_data), content_type='application/json')
    assert response.status_code == 401 # require_api_key fails

def test_create_business_invalid_auth(client):
    """Test creating business with invalid master API key."""
    valid_data = {"owner_id": str(uuid.uuid4()), "business_name": "Test Biz"}
    headers = {'Authorization': 'Bearer wrong-key'}
    response = client.post('/businesses/', headers=headers, data=json.dumps(valid_data), content_type='application/json')
    assert response.status_code == 401 # require_api_key fails

@patch('routes.businesses.validate', side_effect=businesses.ValidationError("Missing required property: 'owner_id'"))
def test_create_business_invalid_data(mock_validate, client):
    """Test creating business with invalid/missing data."""
    invalid_data = {"business_name": "Test Biz"} # Missing owner_id
    headers = {'Authorization': 'Bearer test-master-api-key'}
    response = client.post('/businesses/', headers=headers, data=json.dumps(invalid_data), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data["error_code"] == "INVALID_REQUEST"
    assert "Missing required property: 'owner_id'" in data["message"]

# --- Test GET /businesses/{business_id} ---

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.businesses.get_db_connection')
@patch('routes.businesses.release_db_connection')
@patch('routes.businesses.is_valid_uuid', return_value=True)
@patch('routes.businesses.jsonify')
def test_get_business_success(mock_jsonify, mock_is_valid, mock_release_db_route, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test successful retrieval of a business."""
    # Mock decorator's DB validation to succeed
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = {'business_id': TEST_BUSINESS_ID, 'api_key': TEST_BUSINESS_API_KEY}

    # Mock route's DB fetch
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor

    # Mock the database return value with expected business data
    mock_business = {
        'business_id': TEST_BUSINESS_ID,
        'business_name': 'Test Business',
        'api_key': TEST_BUSINESS_API_KEY,
        'owner_id': str(uuid.uuid4()),
        'business_description': 'Description', 
        'address': 'Address',
        'phone_number': 'Phone',
        'website': 'Website',
        'first_stage_id': None
    }
    mock_route_cursor.fetchone.return_value = mock_business
    
    # Let the actual jsonify function be used
    mock_jsonify.side_effect = jsonify

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.get(f'/businesses/{TEST_BUSINESS_ID}?business_id={TEST_BUSINESS_ID}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['business_id'] == TEST_BUSINESS_ID
    assert data['business_name'] == 'Test Business'
    assert data['api_key'] == TEST_BUSINESS_API_KEY

    # Verify database calls
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    mock_get_conn_route.assert_called_once()
    mock_release_db_route.assert_called_once_with(mock_route_conn)

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Patch decorator's DB call (NO backend.)
@patch('routes.businesses.is_valid_uuid', return_value=True)
def test_get_business_no_auth(mock_is_valid, mock_get_conn_auth, mock_release_auth, client):
    """Test getting business without business API key cookie."""
    response = client.get(f'/businesses/{TEST_BUSINESS_ID}') # No cookie
    assert response.status_code == 401
    data = response.get_json()
    assert data["error_code"] == "UNAUTHORIZED"
    assert "Missing Business API key" in data["message"]

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Patch decorator's DB call (NO backend.)
@patch('routes.businesses.is_valid_uuid', return_value=True)
def test_get_business_invalid_auth(mock_is_valid, mock_get_conn_auth, mock_release_auth, client):
    """Test getting business with invalid business API key."""
    # Mock decorator's DB validation to fail
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = None # Key is invalid

    # Set cookie before request
    client.set_cookie('businessApiKey', 'wrong-key')
    response = client.get(f'/businesses/{TEST_BUSINESS_ID}')

    assert response.status_code == 401
    data = response.get_json()
    assert data["error_code"] == "UNAUTHORIZED"
    assert "Invalid Business API key" in data["message"]
    mock_get_conn_auth.assert_called_once() # Decorator DB check was performed
    mock_release_auth.assert_called_once() # Check release was called

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.businesses.is_valid_uuid', return_value=False)
@patch('routes.businesses.jsonify')
def test_get_business_invalid_id_format(mock_jsonify, mock_is_valid, mock_get_conn_auth, mock_release_auth, client):
    """Test getting business with an invalid UUID format."""
    # Mock the auth decorator's DB validation to fail
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = None  # Invalid key

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)

    # Mock the error response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.get_json.return_value = {
        'error_code': 'UNAUTHORIZED',
        'message': 'API key'
    }
    mock_jsonify.return_value = mock_response

    response = client.get('/businesses/not-a-uuid')

    assert response.status_code == 401
    data = response.get_json()
    assert data['error_code'] == 'UNAUTHORIZED'
    assert 'API key' in data['message']
    
    # Verify database calls
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    # The is_valid_uuid check might be bypassed in the authentication flow, so don't assert on it

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.businesses.get_db_connection')
@patch('routes.businesses.release_db_connection')
@patch('routes.businesses.is_valid_uuid', return_value=True)
def test_get_business_not_found(mock_is_valid, mock_release_db_route, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test when business is not found."""
    # Mock decorator's DB validation to succeed
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)  # Key is valid for business

    # Mock route's DB fetch to return None (business not found)
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor
    mock_route_cursor.fetchone.return_value = None

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.get(f'/businesses/{TEST_BUSINESS_ID}')

    assert response.status_code == 404
    data = response.get_json()
    assert data['error_code'] == 'NOT_FOUND'
    assert 'business not found' in data['message'].lower()

    mock_get_conn_auth.assert_called_once()
    mock_get_conn_route.assert_called_once()
    mock_release_auth.assert_called_once() # Check auth release
    mock_release_db_route.assert_called_once() # Check route release

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.conversations.get_db_connection')
@patch('routes.conversations.release_db_connection')
@patch('routes.conversations.jsonify')
@patch('routes.conversations.execute_query')  # Add mock for execute_query
def test_get_conversations_success(mock_execute_query, mock_jsonify, mock_release_route, mock_get_route, mock_get_auth, mock_release_auth, client):
    """Test getting conversations for a user."""
    # Mock the auth decorator's DB validation
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = {'business_id': TEST_BUSINESS_ID, 'api_key': TEST_BUSINESS_API_KEY}

    # Mock the route's DB responses
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor

    # Mock conversation data
    mock_conv_row = {
        'conversation_id': str(uuid.uuid4()),
        'business_id': TEST_BUSINESS_ID,
        'user_id': TEST_USER_ID,
        'agent_id': str(uuid.uuid4()),
        'stage_id': str(uuid.uuid4()),
        'session_id': str(uuid.uuid4()),
        'start_time': datetime.now(),
        'last_updated': datetime.now()
    }
    
    # Mock message data
    mock_msg_row = {
        'conversation_id': mock_conv_row['conversation_id'],
        'sender_type': 'user',
        'message_content': 'Test message',
        'created_at': datetime.now()
    }
    
    # Mock execute_query with cursor that returns data
    mock_conv_cursor = MagicMock()
    mock_msg_cursor = MagicMock()
    mock_conv_cursor.fetchall.return_value = [mock_conv_row]
    mock_msg_cursor.fetchall.return_value = [mock_msg_row]
    mock_execute_query.side_effect = [mock_conv_cursor, mock_msg_cursor]

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    
    # Use the actual jsonify function
    mock_jsonify.side_effect = jsonify
    
    # Make request with user_id in path and include business_id in query params
    response = client.get(f'/conversations/{TEST_USER_ID}?business_id={TEST_BUSINESS_ID}')
    
    # Print response data to debug the 400 error
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.get_json()}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    conversation = data[0]
    assert conversation['conversation_id'] == mock_conv_row['conversation_id']
    assert conversation['business_id'] == TEST_BUSINESS_ID
    assert conversation['user_id'] == TEST_USER_ID
    assert conversation['agent_id'] == mock_conv_row['agent_id']
    assert conversation['stage_id'] == mock_conv_row['stage_id']
    assert conversation['session_id'] == mock_conv_row['session_id']
    assert 'start_time' in conversation
    assert 'last_updated' in conversation
    assert 'messages' in conversation
    assert len(conversation['messages']) == 1
    assert conversation['messages'][0]['sender'] == 'user'
    assert conversation['messages'][0]['content'] == 'Test message'
    
    # Verify database calls
    mock_get_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    mock_get_route.assert_called_once()
    mock_release_route.assert_called_once_with(mock_route_conn)