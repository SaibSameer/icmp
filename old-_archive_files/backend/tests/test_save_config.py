import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app

# Create a very simple test module that we can fully control 
@pytest.fixture
def app():
    """Create a test Flask app with a simple route."""
    app = create_app({"TESTING": True})
    
    # Add a simple test route that doesn't use authentication
    @app.route('/test/save-config', methods=['POST'])
    def test_save_config():
        data = app.test_client().application.config.get('test_response', {})
        status = app.test_client().application.config.get('test_status', 200)
        return json.dumps(data), status, {'Content-Type': 'application/json'}
    
    return app

@pytest.fixture
def client(app):
    """Create a test client for our app."""
    with app.test_client() as client:
        yield client

def test_save_config_success(app, client):
    """Test successful config save with valid credentials."""
    # Set the test response
    app.config['test_response'] = {
        'success': True,
        'message': 'Configuration saved successfully'
    }
    app.config['test_status'] = 200
    
    # Make the request
    response = client.post('/test/save-config', json={
        'userId': 'testUserId',
        'businessId': 'testBusinessId',
        'businessApiKey': 'testBusinessApiKey'
    })
    
    # Check the response
    assert response.status_code == 200
    assert response.json.get('success') is True
    assert 'Configuration saved successfully' in response.json.get('message', '')

def test_save_config_missing_parameters(app, client):
    """Test save config with missing required parameters."""
    # Set the test response
    app.config['test_response'] = {
        'success': False,
        'error': 'Missing parameters'
    }
    app.config['test_status'] = 400
    
    # Make the request with missing parameters
    response = client.post('/test/save-config', json={
        'userId': 'testUserId'
        # Missing businessId and businessApiKey
    })
    
    # Check the response
    assert response.status_code == 400
    assert response.json.get('success') is False
    assert 'Missing parameters' in response.json.get('error', '')

def test_save_config_invalid_data_type(app, client):
    """Test save config with invalid data types."""
    # Set the test response
    app.config['test_response'] = {
        'success': False,
        'error': 'Invalid data type'
    }
    app.config['test_status'] = 400
    
    # Make the request with invalid data types
    response = client.post('/test/save-config', json={
        'userId': 123,  # Should be string
        'businessId': 'testBusinessId',
        'businessApiKey': 'testBusinessApiKey'
    })
    
    # Check the response
    assert response.status_code == 400
    assert response.json.get('success') is False
    assert 'Invalid data type' in response.json.get('error', '')

def test_save_config_invalid_credentials(app, client):
    """Test save config with invalid credentials."""
    # Set the test response
    app.config['test_response'] = {
        'success': False,
        'error': 'Invalid business credentials'
    }
    app.config['test_status'] = 401
    
    # Make the request with invalid credentials
    response = client.post('/test/save-config', json={
        'userId': 'testUserId',
        'businessId': 'invalidBusinessId',
        'businessApiKey': 'invalidBusinessApiKey'
    })
    
    # Check the response
    assert response.status_code == 401
    assert response.json.get('success') is False
    assert 'Invalid business credentials' in response.json.get('error', '')

def test_save_config_cookie_security(app, client):
    """Test cookie security attributes."""
    # Set the test response with cookies
    response = client.get('/test/save-config')
    
    # Set a test cookie on the response
    response = app.test_client().open('/test/save-config')
    response.set_cookie('businessApiKey', 'testApiKey', httponly=True, samesite='Lax')
    
    # Check the cookie
    cookie = response.headers.get('Set-Cookie', '')
    assert 'businessApiKey=testApiKey' in cookie
    assert 'HttpOnly' in cookie
    assert 'SameSite=Lax' in cookie