# tests/test_message_handling.py
import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from jsonschema import ValidationError
from auth import require_business_api_key
from create_default_stage import create_default_stage

# Mock the blueprint and routes
from routes import message_handling
from openai_helper import call_openai

# --- Fixtures ---

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "SCHEMAS": {} # Mock schemas config if needed by route
    })
    app.register_blueprint(message_handling.bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Test Data ---

TEST_BUSINESS_ID = str(uuid.uuid4())
TEST_USER_ID = str(uuid.uuid4())
TEST_BUSINESS_API_KEY = "test-biz-api-key-messages"
TEST_CONVERSATION_ID = uuid.UUID('fedcba98-12ab-34cd-56ef-fedcba987654')
TEST_SESSION_ID = uuid.uuid4()

VALID_MESSAGE_DATA = {
    "business_id": TEST_BUSINESS_ID,
    "user_id": TEST_USER_ID,
    "message": "Hello, I need help."
}

# Mocked stage config data (as JSON strings, like from DB)
MOCK_STAGE_SELECTION_CONFIG_JSON = json.dumps({
    "template_text": "Select intent for: {message} Context: {context}",
    "model_settings": {}
})
MOCK_STAGE_EXTRACTION_CONFIG_JSON = json.dumps({
    "template_text": "Extract from: {message} Stage: {stage}",
    "model_settings": {}
})
MOCK_STAGE_GENERATION_CONFIG_JSON = json.dumps({
    "template_text": "Generate response for: {message} Data: {extracted_data}",
    "model_settings": {}
})

# Mock stage row with all required columns
MOCK_STAGE_ROW = (
    "3859ab20-49e2-4293-a32c-d0b1d276d02a",  # stage_id
    "Test Stage",                            # stage_name
    "fe8a0380-e797-4a3e-9fdc-8fa6262154d0",  # stage_selection_template_id
    "62b0894d-1ae0-47b8-be7d-4ca70159c5a5",  # data_extraction_template_id 
    "5ed9c7fa-3d21-4467-bd9d-56dc74b8e1f7"   # response_generation_template_id
)

# Mock stage result for get_stage_for_message
MOCK_STAGE_RESULT = (
    "3859ab20-49e2-4293-a32c-d0b1d276d02a",  # stage_id
    "fe8a0380-e797-4a3e-9fdc-8fa6262154d0",  # selection_template_id
    "62b0894d-1ae0-47b8-be7d-4ca70159c5a5",  # extraction_template_id
    "5ed9c7fa-3d21-4467-bd9d-56dc74b8e1f7"   # response_template_id
)

# Mock templates returned from the database query
MOCK_TEMPLATES = [
    ("fe8a0380-e797-4a3e-9fdc-8fa6262154d0", "Select intent for: {message} Context: {context}", "selection", []),
    ("62b0894d-1ae0-47b8-be7d-4ca70159c5a5", "Extract from: {message} Stage: {stage}", "extraction", []),
    ("5ed9c7fa-3d21-4467-bd9d-56dc74b8e1f7", "Generate response for: {message} Data: {extracted_data}", "response", [])
]

# --- Tests for POST /message ---

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Decorator DB check
@patch('routes.message_handling.get_db_connection') # Route DB check
@patch('routes.message_handling.release_db_connection')
@patch('ai.llm_service.LLMService.generate_response') # LLM service generate_response
@patch('routes.message_handling.validate') # Request validation
def test_handle_message_success(mock_validate, mock_generate_response, mock_release_db_route, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test successful message handling and OpenAI response."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)

    # Route DB fetch stage config success
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor

    # Configure mock cursor to return different results based on the query
    def mock_fetchone_side_effect(*args, **kwargs):
        # For stage_id query in get_stage_for_message
        if "SELECT stage_id FROM conversation_stages" in mock_route_cursor.execute.call_args[0][0]:
            return ("3859ab20-49e2-4293-a32c-d0b1d276d02a",)
        # For template IDs query in get_stage_for_message
        elif "SELECT stage_id, selection_template_id, extraction_template_id, response_template_id" in mock_route_cursor.execute.call_args[0][0]:
            return MOCK_STAGE_RESULT
        # Default case
        return MOCK_STAGE_ROW

    mock_route_cursor.fetchone.side_effect = mock_fetchone_side_effect
    mock_route_cursor.fetchall.return_value = MOCK_TEMPLATES

    # Mock LLM response
    mock_generate_response.return_value = "final_ai_response"

    valid_data = {
        "user_id": TEST_USER_ID,
        "business_id": TEST_BUSINESS_ID,
        "conversation_id": str(TEST_CONVERSATION_ID),
        "message": "Hello AI",
        "session_id": str(TEST_SESSION_ID)
    }

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.post(
        '/message',
        data=json.dumps(valid_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["response"] == "final_ai_response"
    assert data["conversation_id"] == str(TEST_CONVERSATION_ID)

    mock_validate.assert_called_once_with(instance=valid_data, schema=message_handling.message_schema)
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once()
    mock_get_conn_route.assert_called_once()
    # Verify LLM service was called
    mock_generate_response.assert_called()

def test_handle_message_no_auth(client):
    """Test message handling without business key."""
    response = client.post(
        '/message',
        data=json.dumps(VALID_MESSAGE_DATA),
        content_type='application/json'
    )
    assert response.status_code == 401
    assert "Missing Business API key" in response.get_json()["message"]

@patch('routes.message_handling.validate', side_effect=ValidationError("Invalid format"))
def test_handle_message_invalid_data(mock_validate, client):
    """Test message handling with invalid request body."""
    # Set cookie before request (needed for decorator to pass)
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.post(
        '/message',
        data=json.dumps({"msg": "wrong structure"}),
        content_type='application/json'
    )

    assert response.status_code == 400
    # Decorator fails first because business_id is missing from invalid data
    assert "Business ID is required" in response.get_json().get("message", "")
    mock_validate.assert_not_called() # Validation likely not reached

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Decorator DB check
@patch('routes.message_handling.get_db_connection') # Route DB check
@patch('routes.message_handling.release_db_connection')
@patch('ai.llm_service.LLMService.generate_response', side_effect=Exception("OpenAI API Error")) # Simulate LLM error
@patch('routes.message_handling.validate')
def test_handle_message_openai_error(mock_validate, mock_generate_response, mock_release_db_route, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test message handling when OpenAI call fails."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor
    mock_route_cursor.fetchone.return_value = MOCK_STAGE_ROW
    mock_route_cursor.fetchall.return_value = MOCK_TEMPLATES

    valid_data = {
        "user_id": TEST_USER_ID,
        "business_id": TEST_BUSINESS_ID,
        "conversation_id": str(TEST_CONVERSATION_ID),
        "message": "Hello AI",
        "session_id": str(TEST_SESSION_ID)
    }

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.post(
        '/message',
        data=json.dumps(valid_data),
        content_type='application/json'
    )

    # The implementation returns a 500 error when the LLM service fails
    assert response.status_code == 500
    
    # Verify response contains error information
    data = response.get_json()
    assert data["success"] == False
    assert "error" in data
    assert "OpenAI API Error" in data["error"]
    
    # Verify LLM service was called
    mock_generate_response.assert_called()

# Add tests for JSON parsing errors in stage config, etc.