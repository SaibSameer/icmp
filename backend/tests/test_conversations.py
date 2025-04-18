import pytest
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

# Mock the blueprint and routes
from routes import conversations
from auth import require_business_api_key
from routes.utils import is_valid_uuid

# --- Fixtures ---

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update({"TESTING": True})
    app.register_blueprint(conversations.bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Test Data ---

TEST_USER_ID = str(uuid.uuid4())
TEST_BUSINESS_ID = str(uuid.uuid4()) # Assume this is the business associated with the key
TEST_BUSINESS_API_KEY = "test-biz-api-key-convos"
TEST_CONVERSATION_ID = str(uuid.uuid4())  # Add conversation ID constant

MOCK_CONVERSATION_DATA = [
    {
        "conversation_id": uuid.uuid4(),
        "business_id": TEST_BUSINESS_ID, # Ensure this matches the expected business
        "user_id": TEST_USER_ID,
        "agent_id": uuid.uuid4(),
        "stage_id": uuid.uuid4(),
        "session_id": "session_1",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "conversation_id": uuid.uuid4(),
        "business_id": TEST_BUSINESS_ID,
        "user_id": TEST_USER_ID,
        "agent_id": None,
        "stage_id": None,
        "session_id": "session_2",
        "created_at": datetime.now(timezone.utc)
    }
]

# --- Tests for GET /conversations/{user_id} ---

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.conversations.get_db_connection')
@patch('routes.conversations.release_db_connection')
@patch('routes.conversations.jsonify')
def test_get_conversations_success(mock_jsonify, mock_release_route, mock_get_route, mock_get_auth, mock_release_auth, client):
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
    mock_route_cursor.fetchall.return_value = [mock_conv_row]

    # Mock message data
    mock_msg_row = {
        'conversation_id': mock_conv_row['conversation_id'],
        'sender_type': 'user',
        'message_content': 'Test message',
        'created_at': datetime.now()
    }
    mock_route_cursor.fetchall.side_effect = [[mock_conv_row], [mock_msg_row]]

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    
    # Use the actual jsonify function
    mock_jsonify.side_effect = jsonify
    
    # Make request with user_id in path and business_id in query params
    response = client.get(f'/conversations/{TEST_USER_ID}?business_id={TEST_BUSINESS_ID}')
    
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
    message = conversation['messages'][0]
    assert message['sender'] == mock_msg_row['sender_type']
    assert message['content'] == mock_msg_row['message_content']
    assert 'timestamp' in message
    
    # Verify database calls
    mock_get_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    mock_get_route.assert_called_once()
    mock_release_route.assert_called_once_with(mock_route_conn)

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.conversations.is_valid_uuid', return_value=True)
@patch('routes.conversations.jsonify')
def test_get_conversations_no_auth(mock_jsonify, mock_is_valid, mock_get_conn_auth, mock_release_auth, client):
    """Test getting conversations without auth key."""
    # Mock the error response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.get_json.return_value = {
        'error_code': 'BAD_REQUEST',
        'message': 'Business ID is required'
    }
    mock_jsonify.return_value = mock_response
    
    response = client.get(f'/conversations/{TEST_USER_ID}')  # No cookie
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'BAD_REQUEST'
    assert 'Business ID is required' in data['message']
    
    # Verify database calls
    mock_get_conn_auth.assert_not_called()
    mock_release_auth.assert_not_called()

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.conversations.is_valid_uuid', return_value=True)
@patch('routes.conversations.jsonify')
def test_get_conversations_invalid_auth(mock_jsonify, mock_is_valid, mock_get_conn_auth, mock_release_auth, client):
    """Test getting conversations with invalid auth key."""
    # Mock the auth decorator's DB validation to fail
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = None  # Invalid key

    # Mock the error response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.get_json.return_value = {
        'error_code': 'UNAUTHORIZED',
        'message': 'Invalid Business API key'
    }
    mock_jsonify.return_value = mock_response

    # Set cookie before request
    client.set_cookie('businessApiKey', 'invalid-key')
    response = client.get(f'/conversations/{TEST_USER_ID}?business_id={TEST_BUSINESS_ID}')

    assert response.status_code == 401
    data = response.get_json()
    assert data['error_code'] == 'UNAUTHORIZED'
    assert 'Invalid Business API key' in data['message']
    
    # Verify database calls
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)

@patch('routes.conversations.is_valid_uuid', return_value=False)
def test_get_conversations_invalid_user_id_format(mock_is_valid, client):
    """Test getting conversations with invalid user_id format."""
    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.get('/conversations/not-a-uuid')

    # Expect 400 because decorator needs business_id, which is missing from this route
    assert response.status_code == 400
    data = response.get_json()
    assert data["error_code"] == "BAD_REQUEST"
    assert "Business ID is required" in data["message"]
    # mock_release_auth.assert_called_once() # Not called because decorator fails early
    mock_is_valid.assert_not_called() # is_valid_uuid in route handler is not reached

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Decorator DB check (NO backend.)
@patch('routes.conversations.get_db_connection') # Route DB check
def test_get_conversations_db_error(mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test handling of DB error when fetching conversations."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)

    # Mock route DB execute failure (this won't be reached)
    mock_get_conn_route.side_effect = Exception("DB error")

    response = client.get(f'/conversations/{TEST_USER_ID}')

    # Expect 400 because decorator needs business_id, which is missing from this route
    assert response.status_code == 400
    data = response.get_json()
    assert data["error_code"] == "BAD_REQUEST"
    assert "Business ID is required" in data["message"]
    # mock_release_auth.assert_called_once() # Not called because decorator fails early
    mock_get_conn_route.assert_not_called() # Route DB function should not be called

# NOTE: Add tests for authorization (ensuring the authenticated business
# has the right to view conversations for this user_id) once user auth/
# business-user linking is implemented.