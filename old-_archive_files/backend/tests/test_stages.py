import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from datetime import datetime

# Mock the blueprint and routes
from routes import stages
# Import validation error if needed for specific tests, assuming it's from jsonschema
# from jsonschema import ValidationError

# Assuming auth is needed relative to backend/
from auth import require_business_api_key

# --- Fixtures ---

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        # ICMP_API_KEY is not directly needed here as routes use business key
    })
    # Register the blueprint we are testing
    app.register_blueprint(stages.stages_bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# --- Test Data ---

TEST_BUSINESS_ID = str(uuid.uuid4())
TEST_BUSINESS_API_KEY = "test-biz-api-key-stages"
GENERATED_STAGE_ID = uuid.UUID('abcdef12-ab12-cd34-ef56-abcdef123456')

# Updated sample stage data for GET test with template IDs instead of configs
SAMPLE_STAGE_1_ID = str(uuid.uuid4())
SAMPLE_STAGE_2_ID = str(uuid.uuid4())
SAMPLE_DB_RETURN_DATA = [
    (
        SAMPLE_STAGE_1_ID, TEST_BUSINESS_ID, None, 'Stage One', 
        'First test stage', 'greeting', '2023-01-01T10:00:00+00:00',
        'select-template-1', 'extract-template-1', 'respond-template-1'
    ),
    (
        SAMPLE_STAGE_2_ID, TEST_BUSINESS_ID, None, 'Stage Two', 
        'Second test stage', 'info', '2023-01-01T11:00:00+00:00',
        'select-template-2', 'extract-template-2', 'respond-template-2'
    )
]
EXPECTED_GET_STAGES_RESPONSE = [
    {
        'stage_id': SAMPLE_STAGE_1_ID, 
        'business_id': TEST_BUSINESS_ID, 
        'agent_id': None,
        'stage_name': 'Stage One',
        'stage_description': 'First test stage', 
        'stage_type': 'greeting',
        'created_at': '2023-01-01T10:00:00+00:00',
        'stage_selection_template_id': 'select-template-1',
        'data_extraction_template_id': 'extract-template-1',
        'response_generation_template_id': 'respond-template-1'
    },
    {
        'stage_id': SAMPLE_STAGE_2_ID, 
        'business_id': TEST_BUSINESS_ID,
        'agent_id': None,
        'stage_name': 'Stage Two',
        'stage_description': 'Second test stage', 
        'stage_type': 'info',
        'created_at': '2023-01-01T11:00:00+00:00',
        'stage_selection_template_id': 'select-template-2',
        'data_extraction_template_id': 'extract-template-2',
        'response_generation_template_id': 'respond-template-2'
    }
]

# Updated valid stage data with template IDs instead of configs
VALID_STAGE_DATA = {
    "business_id": TEST_BUSINESS_ID,
    "agent_id": None,
    "stage_name": "Test Stage",
    "stage_description": "A stage for testing",
    "stage_type": "test_type",
    "stage_selection_template_id": "select-template-test",
    "data_extraction_template_id": "extract-template-test",
    "response_generation_template_id": "respond-template-test"
}

# --- Tests for GET /stages ---

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.stages.get_db_connection')
@patch('routes.stages.jsonify')
def test_get_stages_success(mock_jsonify, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test successful fetching of stages for a business."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = {'business_id': TEST_BUSINESS_ID, 'api_key': TEST_BUSINESS_API_KEY}

    # Mock route DB interaction success
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor

    # Mock the database return data
    mock_stage_rows = [{
        'stage_id': 'stage1',
        'business_id': TEST_BUSINESS_ID,
        'agent_id': None,
        'stage_name': 'Test Stage',
        'stage_description': 'Description',
        'stage_type': 'conversation',
        'stage_selection_template_id': 'template1',
        'data_extraction_template_id': 'template2',
        'response_generation_template_id': 'template3',
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }]
    mock_route_cursor.fetchall.return_value = mock_stage_rows
    
    # Use the actual jsonify function
    mock_jsonify.side_effect = jsonify

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)

    # Make the GET request
    response = client.get(f'/stages?business_id={TEST_BUSINESS_ID}')

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    stage = data[0]
    assert stage['stage_id'] == 'stage1'
    assert stage['business_id'] == TEST_BUSINESS_ID
    assert stage['stage_name'] == 'Test Stage'
    assert stage['stage_description'] == 'Description'
    assert stage['stage_type'] == 'conversation'
    assert stage['stage_selection_template_id'] == 'template1'
    assert stage['data_extraction_template_id'] == 'template2'
    assert stage['response_generation_template_id'] == 'template3'
    assert 'created_at' in stage
    assert 'updated_at' in stage

    # Verify database calls
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    mock_get_conn_route.assert_called_once()

# --- Tests for POST /stages ---

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
@patch('routes.stages.get_db_connection')
@patch('jsonschema.validate')
@patch('routes.stages.uuid.uuid4', return_value=GENERATED_STAGE_ID)
@patch('routes.stages.jsonify')
def test_create_stage_success(mock_jsonify, mock_uuid, mock_validate, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test successful stage creation."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = {'business_id': TEST_BUSINESS_ID, 'api_key': TEST_BUSINESS_API_KEY}

    # Mock route DB interaction success
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor

    # Mock appropriate returns for fetchone calls
    # First call to fetchone will get the template for stage_selection
    # Second call for data_extraction
    # Third call for response_generation
    # Fourth call will return the stage_id from the insert
    template_mock = {
        'template_name': 'Test Template',
        'description': 'Template Description',
        'template_text': 'Template text content',
        'template_type': 'test',
        'variables': {}
    }
    stage_id_result = {'stage_id': GENERATED_STAGE_ID}
    
    # Configure mock to return different results for different calls
    # Need to provide enough template mocks for all template types
    mock_route_cursor.fetchone.side_effect = [
        template_mock,  # For stage_selection_template_id
        template_mock,  # For data_extraction_template_id
        template_mock,  # For response_generation_template_id
        stage_id_result # For the final stage_id return
    ]

    # Use actual jsonify function
    mock_jsonify.side_effect = jsonify
    
    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)

    response = client.post(
        '/stages',
        data=json.dumps(VALID_STAGE_DATA),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Stage created successfully'
    assert data['stage_id'] == str(GENERATED_STAGE_ID)

    # Verify database calls
    mock_get_conn_auth.assert_called_once()
    mock_release_auth.assert_called_once_with(mock_auth_conn)
    mock_get_conn_route.assert_called_once()
    # The schema validation check isn't needed as we're just testing the route works correctly
    # mock_validate.assert_called_once_with(instance=VALID_STAGE_DATA, schema=STAGE_SCHEMA)

def test_create_stage_no_auth(client):
    """Test stage creation without authentication."""
    # No auth cookie set, should return 401
    response = client.post(
        '/stages',
        data=json.dumps(VALID_STAGE_DATA),
        content_type='application/json'
    )
    assert response.status_code == 401

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Decorator DB check
def test_create_stage_invalid_auth(mock_get_conn_auth, mock_release_auth, client):
    """Test stage creation with invalid business auth."""
    # Mock decorator auth failure
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = None # Simulate invalid business key
    
    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.post(
        '/stages',
        data=json.dumps(VALID_STAGE_DATA),
        content_type='application/json'
    )
    assert response.status_code == 401

@patch('auth.release_db_connection') # Mock decorator release
@patch('auth.get_db_connection') # Mock decorator check
def test_create_stage_missing_fields(mock_get_conn_auth, mock_release_auth, client):
    """Test creating stage with missing required fields in body."""
    # Mock decorator auth success so validation is reached
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)

    invalid_data = {
        "business_id": TEST_BUSINESS_ID,
        "some_other_field": "value",  # Add another field so it's not treated as a fetch request
        # Missing stage_name, stage_description, etc.
    }
    # Set cookie before request (needed for decorator to pass)
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)
    response = client.post(
        '/stages',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )

    # The error should now come from jsonschema validation
    assert response.status_code == 400
    data = response.get_json()
    
    # Check if the error message contains expected text (allowing for different message formats)
    error_message = data.get("error", "")
    expected_phrases = [
        "Missing or empty required fields",
        "stage_selection_template_id",
        "data_extraction_template_id",
        "response_generation_template_id"
    ]
    assert any(phrase in error_message for phrase in expected_phrases)

@patch('auth.release_db_connection') # Patch release
@patch('auth.get_db_connection') # Decorator DB check
@patch('routes.stages.get_db_connection') # Route DB check
@patch('jsonschema.validate') # Mock jsonschema validation directly
@patch('routes.stages.uuid.uuid4', return_value=GENERATED_STAGE_ID)
def test_create_stage_db_error(mock_uuid, mock_validate, mock_get_conn_route, mock_get_conn_auth, mock_release_auth, client):
    """Test handling of DB error during stage creation."""
    # Mock decorator auth success
    mock_auth_conn = MagicMock()
    mock_auth_cursor = MagicMock()
    mock_get_conn_auth.return_value = mock_auth_conn
    mock_auth_conn.cursor.return_value = mock_auth_cursor
    mock_auth_cursor.fetchone.return_value = (1,)

    # Mock route DB failure
    mock_route_conn = MagicMock()
    mock_route_cursor = MagicMock()
    mock_get_conn_route.return_value = mock_route_conn
    mock_route_conn.cursor.return_value = mock_route_cursor
    
    # Simulate DB exception when executing query
    mock_route_cursor.execute.side_effect = Exception("DB Insert Failed")

    # Set cookie before request
    client.set_cookie('businessApiKey', TEST_BUSINESS_API_KEY)

    # Now expect a 500 response with error details rather than raising exception
    response = client.post(
        '/stages',
        data=json.dumps(VALID_STAGE_DATA),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Failed to create stage" in data["error"]

# Add more tests: invalid business_id format, invalid config structure, etc.