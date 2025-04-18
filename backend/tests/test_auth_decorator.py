import pytest
from flask import Flask, request, jsonify
from auth import require_api_key
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['ICMP_API_KEY'] = 'test_api_key_123'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_valid_api_key_in_cookie(app, client):
    @app.route('/test', methods=['POST'])
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    # Set cookie before request
    client.set_cookie('icmpApiKey', 'test_api_key_123')
    response = client.post('/test', json={'data': 'test'})

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'

def test_valid_api_key_in_header(app, client):
    @app.route('/test', methods=['POST'])
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    response = client.post('/test',
                         headers={'Authorization': 'Bearer test_api_key_123'},
                         json={'data': 'test'})
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'success'

def test_invalid_api_key(app, client):
    @app.route('/test', methods=['POST'])
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    # Set cookie before request
    client.set_cookie('icmpApiKey', 'wrong_key')
    response = client.post('/test', json={'data': 'test'})

    assert response.status_code == 401
    assert json.loads(response.data)['error_code'] == 'UNAUTHORIZED'

def test_missing_api_key(app, client):
    @app.route('/test', methods=['POST'])
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    response = client.post('/test',
                         json={'data': 'test'})
    assert response.status_code == 401
    assert json.loads(response.data)['error_code'] == 'UNAUTHORIZED'

def test_missing_config_api_key(app):
    app = Flask(__name__)
    # Don't set ICMP_API_KEY in config

    @app.route('/test', methods=['POST'])
    @require_api_key
    def test_route():
        return jsonify({"message": "success"})

    client = app.test_client()
    # Set cookie before request
    client.set_cookie('icmpApiKey', 'test_api_key_123')
    response = client.post('/test', json={'data': 'test'})

    assert response.status_code == 500
    assert json.loads(response.data)['error_code'] == 'CONFIG_ERROR'

def test_validate_config_with_valid_credentials(app, client):
    @app.route('/validate_config', methods=['POST'])
    @require_api_key
    def validate_config():
        data = request.get_json()
        return jsonify({
            'isValid': True,
            'message': 'Configuration validated successfully'
        })

    # Set cookie before request
    client.set_cookie('icmpApiKey', 'test_api_key_123')
    response = client.post('/validate_config',
                         json={
                             # 'apiKey': 'test_api_key_123', # Assuming master key is from cookie
                             'userId': 'test_user',
                             'businessId': 'test_business',
                             'businessApiKey': 'test_business_key'
                         })

    assert response.status_code == 200
    assert json.loads(response.data)['isValid'] == True