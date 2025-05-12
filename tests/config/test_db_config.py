"""
Configuration settings for the test database.
"""

import os

# Test database configuration
TEST_DB_CONFIG = {
    'name': os.environ.get('TEST_DB_NAME', 'icmp_test_db'),
    'user': os.environ.get('TEST_DB_USER', 'postgres'),
    'password': os.environ.get('TEST_DB_PASSWORD', 'postgres'),
    'host': os.environ.get('TEST_DB_HOST', 'localhost'),
    'port': os.environ.get('TEST_DB_PORT', '5432')
}

# Test database connection string
TEST_DB_URL = f"postgresql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['name']}"

# Test database pool settings
TEST_DB_POOL_CONFIG = {
    'min_size': 1,
    'max_size': 10,
    'timeout': 30
}

# Test data settings
TEST_DATA_CONFIG = {
    'seed_data': True,  # Whether to seed test data
    'cleanup_after_tests': True,  # Whether to clean up after tests
    'use_transactions': True  # Whether to use transactions for test isolation
} 