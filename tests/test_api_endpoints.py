import pytest
from flask import json
from backend.error_handling import (
    ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError
)

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_validation_error_endpoint(client):
    """Test endpoint that raises validation error."""
    response = client.post('/api/users', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'field_errors' in data['error']['details']

def test_authentication_error_endpoint(client):
    """Test endpoint that requires authentication."""
    response = client.get('/api/protected')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error']['code'] == 'AUTHENTICATION_ERROR'

def test_authorization_error_endpoint(client):
    """Test endpoint that requires admin access."""
    # First authenticate
    client.post('/api/auth/login', json={
        'email': 'user@example.com',
        'password': 'password'
    })
    
    # Then try to access admin endpoint
    response = client.get('/api/admin')
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error']['code'] == 'AUTHORIZATION_ERROR'

def test_not_found_error_endpoint(client):
    """Test endpoint that returns not found error."""
    response = client.get('/api/users/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error']['code'] == 'NOT_FOUND'

def test_database_error_endpoint(client):
    """Test endpoint that raises database error."""
    response = client.post('/api/users', json={
        'email': 'invalid@example.com',
        'password': 'password'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error']['code'] == 'DATABASE_ERROR'

def test_service_error_endpoint(client):
    """Test endpoint that raises service error."""
    response = client.post('/api/payment', json={
        'amount': 100,
        'currency': 'USD'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error']['code'] == 'SERVICE_ERROR'

def test_error_tracking_in_endpoints(client, error_tracker):
    """Test error tracking in API endpoints."""
    # Make request that will cause an error
    response = client.get('/api/nonexistent')
    
    # Check error was tracked
    stats = error_tracker.get_error_stats()
    assert 'NOT_FOUND' in stats
    assert stats['NOT_FOUND'] > 0

def test_error_response_format_consistency(client):
    """Test error response format consistency across endpoints."""
    # Test validation error
    response = client.post('/api/users', json={})
    data = json.loads(response.data)
    assert 'error' in data
    assert 'code' in data['error']
    assert 'message' in data['error']
    assert 'details' in data['error']
    
    # Test authentication error
    response = client.get('/api/protected')
    data = json.loads(response.data)
    assert 'error' in data
    assert 'code' in data['error']
    assert 'message' in data['error']
    assert 'details' in data['error']
    
    # Test not found error
    response = client.get('/api/nonexistent')
    data = json.loads(response.data)
    assert 'error' in data
    assert 'code' in data['error']
    assert 'message' in data['error']
    assert 'details' in data['error']

def test_error_handling_with_invalid_json(client):
    """Test error handling with invalid JSON."""
    response = client.post(
        '/api/users',
        data='invalid json',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'VALIDATION_ERROR'

def test_error_handling_with_missing_required_fields(client):
    """Test error handling with missing required fields."""
    response = client.post('/api/users', json={
        'email': 'test@example.com'
        # Missing password field
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'password' in data['error']['details']['field_errors'] 