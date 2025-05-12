"""
Test configuration and fixtures for the ICMP Events API tests.
"""

import pytest
import os
from unittest.mock import Mock
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask
from backend.app import create_app
from backend.error_handling import ErrorHandler, ErrorTracker
from backend.database.db import get_db_connection

# Set testing environment
os.environ['TESTING'] = 'true'

# Test database configuration
TEST_DB_CONFIG = {
    'dbname': os.getenv('TEST_DB_NAME', 'icmp_test'),
    'user': os.getenv('TEST_DB_USER', 'postgres'),
    'password': os.getenv('TEST_DB_PASSWORD', 'postgres'),
    'host': os.getenv('TEST_DB_HOST', 'localhost'),
    'port': os.getenv('TEST_DB_PORT', '5432')
}

@pytest.fixture(scope='session')
def test_db_pool():
    """Create a test database connection pool."""
    pool = Mock()
    pool.getconn.return_value = Mock()
    return pool

@pytest.fixture(scope='function')
def test_db_connection():
    """Create a test database connection."""
    conn = psycopg2.connect(**TEST_DB_CONFIG, cursor_factory=RealDictCursor)
    yield conn
    conn.close()

@pytest.fixture(scope='function')
def test_db_cursor(test_db_connection):
    """Create a test database cursor."""
    cursor = test_db_connection.cursor()
    yield cursor
    cursor.close()

@pytest.fixture(scope='function')
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.generate.return_value = {
        'text': 'Mock response',
        'confidence': 0.95
    }
    return service

@pytest.fixture(scope='function')
def sample_template():
    """Create a sample template for testing."""
    return {
        'template_id': 'test_template',
        'name': 'Test Template',
        'content': 'Hello {name}, your order {order_id} is ready.',
        'variables': ['name', 'order_id'],
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }

@pytest.fixture(scope='function')
def sample_message():
    """Create a sample message for testing."""
    return {
        'message_id': 'test_message_1',
        'content': 'Hello, my name is John and my order number is 12345',
        'timestamp': datetime.now(),
        'channel': 'whatsapp',
        'sender_id': 'test_user_1'
    }

@pytest.fixture(scope='function')
def sample_business():
    """Create a sample business for testing."""
    return {
        'business_id': 'test_business_1',
        'name': 'Test Business',
        'api_key': 'test_api_key',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }

@pytest.fixture(scope='function')
def sample_stage():
    """Create a sample stage for testing."""
    return {
        'stage_id': 'test_stage_1',
        'name': 'Test Stage',
        'business_id': 'test_business_1',
        'template_id': 'test_template',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db'
    })
    
    # Initialize error handling
    error_handler = ErrorHandler(app)
    error_tracker = ErrorTracker()
    
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def db_connection():
    """Create a database connection for testing."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

@pytest.fixture
def error_tracker():
    """Create an error tracker instance for testing."""
    return ErrorTracker()

@pytest.fixture
def sample_error_data():
    """Sample error data for testing."""
    return {
        'code': 'TEST_ERROR',
        'message': 'Test error message',
        'details': {
            'field_errors': {
                'test_field': 'Test field error'
            },
            'context': 'Test error context'
        }
    } 