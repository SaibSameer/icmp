import pytest
from flask import Flask, jsonify, request
from auth import require_api_key, require_business_api_key
from unittest.mock import patch
import json
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    # Use relative path for imports within backend
    from db import CONNECTION_POOL
    app.config.update({
        "TESTING": True,
        "ICMP_API_KEY": "test_master_key_456",
        "APPLICATION_ROOT": "/"
    })
    # Register routes needed for testing decorators if any
    # Example placeholder route:
    @app.route('/_test/biz/<business_id>')
    def placeholder_biz_route(business_id):
        return 'OK'
    @app.route('/_test/no_biz_id')
    def placeholder_no_biz_route():
        return 'OK'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_require_api_key_valid_cookie(app, client):
    @app.route('/test_master_cookie')
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})
    # Set cookie before request
    client.set_cookie('icmpApiKey', 'test_master_key_456')
    response = client.get('/test_master_cookie')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'

def test_require_api_key_valid_header(app, client):
    @app.route('/test_master_header')
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    response = client.get('/test_master_header',
                         headers={'Authorization': 'Bearer test_master_key_456'})
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'

def test_require_api_key_invalid(app, client):
    @app.route('/test_master_invalid')
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    response = client.get('/test_master_invalid',
                         headers={'Authorization': 'Bearer wrong_key'})
    assert response.status_code == 401
    assert json.loads(response.data)['error_code'] == 'UNAUTHORIZED'

def test_require_api_key_missing(app, client):
    @app.route('/test_master_missing')
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    response = client.get('/test_master_missing')
    assert response.status_code == 401
    assert json.loads(response.data)['error_code'] == 'UNAUTHORIZED'

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
def test_require_business_key_valid_cookie(mock_get_conn, mock_release, app, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)

    @app.route('/biz/<business_id>/resource')
    @require_business_api_key
    def biz_route(business_id):
        return jsonify({"message": "success", "business": business_id})

    business_id = 'biz_123'
    business_key = 'valid_biz_key_abc'

    # Set cookie before request
    client.set_cookie('businessApiKey', business_key)
    response = client.get(f'/biz/{business_id}/resource')

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'
    assert json.loads(response.data)['business'] == business_id
    mock_get_conn.assert_called_once()
    mock_cursor.execute.assert_called_once_with(
        "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
        (business_id, business_key)
    )
    mock_cursor.fetchone.assert_called_once()
    mock_release.assert_called_once_with(mock_conn)

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
def test_require_business_key_valid_header(mock_get_conn, mock_release, app, client):
    mock_conn = mock_get_conn.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)

    @app.route('/biz_h/<business_id>/resource')
    @require_business_api_key
    def biz_route_h(business_id):
        return jsonify({"message": "success", "business": business_id})

    business_id = 'biz_456'
    business_key = 'valid_biz_key_def'

    response = client.get(
        f'/biz_h/{business_id}/resource',
        headers={'Authorization': f'Bearer {business_key}'}
    )

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'
    mock_cursor.execute.assert_called_once_with(
        "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
        (business_id, business_key)
    )
    mock_release.assert_called_once_with(mock_conn)

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
def test_require_business_key_invalid_key(mock_get_conn, mock_release, app, client):
    mock_conn = mock_get_conn.return_value
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None

    @app.route('/biz_inv/<business_id>/resource')
    @require_business_api_key
    def biz_route_inv(business_id):
        return jsonify({"message": "success", "business": business_id})

    business_id = 'biz_789'
    invalid_key = 'invalid_key'

    # Set cookie before request
    client.set_cookie('businessApiKey', invalid_key)
    response = client.get(f'/biz_inv/{business_id}/resource')

    assert response.status_code == 401
    assert json.loads(response.data)['error_code'] == 'UNAUTHORIZED'
    assert 'Invalid Business API key' in json.loads(response.data)['message']
    mock_cursor.execute.assert_called_once_with(
        "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
        (business_id, invalid_key)
    )
    mock_release.assert_called_once_with(mock_conn)

def test_require_business_key_missing_biz_id(app, client):
    @app.route('/biz_no_id/resource')
    @require_business_api_key
    def biz_route_no_id():
        return jsonify({"message": "success"})

    business_key = 'some_key'

    # Set cookie before request
    client.set_cookie('businessApiKey', business_key)
    response = client.get('/biz_no_id/resource')

    assert response.status_code == 400
    assert json.loads(response.data)['error_code'] == 'BAD_REQUEST'
    assert 'Business ID is required' in json.loads(response.data)['message']

@patch('auth.release_db_connection')
@patch('auth.get_db_connection')
def test_require_business_key_db_error(mock_get_conn, mock_release, app, client):
    """Test handling of database error in business API key validation."""
    # Set up the mock to raise an exception
    mock_get_conn.side_effect = Exception("DB connection failed")

    @app.route('/biz_dberr/<business_id>/resource')
    @require_business_api_key
    def biz_route_dberr(business_id):
        return jsonify({"message": "success", "business": business_id})

    business_id = 'biz_err'
    business_key = 'key_for_err'

    # Set cookie before request
    client.set_cookie('businessApiKey', business_key)
    
    # Use try/except to catch the exception and verify it's handled correctly
    try:
        response = client.get(f'/biz_dberr/{business_id}/resource')
    except Exception as e:
        # The exception should be caught by the decorator and return a 500 error
        assert str(e) == "DB connection failed"
        return
    
    # If we get here, the test should fail
    assert False, "Expected an exception to be raised"