# Testing Strategy

## Overview
This document outlines the testing strategy for the ICMP Events API, including unit testing, integration testing, and end-to-end testing approaches.

## Test Types

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic
- Use pytest fixtures for setup

### Integration Tests
- Test component interactions
- Use test database
- Mock external services
- Test API endpoints
- Test Redis integration
- Test template system

### End-to-End Tests
- Test complete workflows
- Use staging environment
- Test real integrations
- Focus on user scenarios
- Test Redis state management
- Test template caching

## Test Organization

### Directory Structure
```
tests/
├── unit/
│   ├── message_processing/
│   ├── template_management/
│   ├── redis/
│   └── services/
├── integration/
│   ├── api/
│   ├── database/
│   ├── redis/
│   └── templates/
└── e2e/
    ├── workflows/
    └── scenarios/
```

### Test Files
- Use `test_` prefix
- Group related tests
- Follow naming conventions
- Include docstrings

## Testing Tools

### pytest
- Main testing framework
- Fixtures for setup
- Parametrized tests
- Assertion helpers

### pytest-cov
- Code coverage reporting
- Coverage thresholds
- HTML reports
- Branch coverage

### pytest-mock
- Mocking utilities
- Patch decorators
- Mock objects
- Spy functions

### pytest-redis
- Redis testing utilities
- Redis fixtures
- Redis mocking
- Redis assertions

## Test Patterns

### Database Testing
```python
@pytest.fixture
def db_connection():
    """Create test database connection."""
    conn = get_test_db_connection()
    yield conn
    conn.close()

def test_database_operation(db_connection):
    """Test database operation."""
    result = db_connection.execute("SELECT 1")
    assert result.fetchone()[0] == 1
```

### Redis Testing
```python
@pytest.fixture
def redis_manager():
    """Create test Redis manager."""
    manager = RedisStateManager(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        ssl=Config.REDIS_SSL,
        max_connections=Config.REDIS_MAX_CONNECTIONS,
        socket_timeout=Config.REDIS_SOCKET_TIMEOUT,
        retry_on_timeout=Config.REDIS_RETRY_ON_TIMEOUT
    )
    yield manager
    manager.clear_all()  # Cleanup

def test_redis_operations(redis_manager):
    """Test Redis operations."""
    # Test set/get
    redis_manager.set_state("test_key", "test_value")
    value = redis_manager.get_state("test_key")
    assert value == "test_value"
    
    # Test hash operations
    redis_manager.set_hash("test_hash", "field", "value")
    hash_value = redis_manager.get_hash("test_hash", "field")
    assert hash_value == "value"
    
    # Test template caching
    redis_manager.cache_template("template_id", {"content": "test"})
    template = redis_manager.get_cached_template("template_id")
    assert template["content"] == "test"
    
    # Test state management
    redis_manager.set_stage_state("conv_id", "stage_id")
    stage = redis_manager.get_stage_state("conv_id")
    assert stage == "stage_id"
```

### Mock Redis
```python
class MockRedis:
    """Mock Redis for testing."""
    def __init__(self):
        self.store = {}
        self.hash_store = {}
        self.template_cache = {}
        self.stage_states = {}
    
    def set_state(self, key, value):
        self.store[key] = value
    
    def get_state(self, key):
        return self.store.get(key)
    
    def delete_state(self, key):
        if key in self.store:
            del self.store[key]
    
    def set_hash(self, key, field, value):
        if key not in self.hash_store:
            self.hash_store[key] = {}
        self.hash_store[key][field] = value
    
    def get_hash(self, key, field):
        return self.hash_store.get(key, {}).get(field)
    
    def delete_hash(self, key, field):
        if key in self.hash_store and field in self.hash_store[key]:
            del self.hash_store[key][field]
    
    def cache_template(self, template_id, template_data):
        self.template_cache[template_id] = template_data
    
    def get_cached_template(self, template_id):
        return self.template_cache.get(template_id)
    
    def set_stage_state(self, conversation_id, stage_id):
        self.stage_states[conversation_id] = stage_id
    
    def get_stage_state(self, conversation_id):
        return self.stage_states.get(conversation_id)
    
    def clear_all(self):
        self.store.clear()
        self.hash_store.clear()
        self.template_cache.clear()
        self.stage_states.clear()

@pytest.fixture
def mock_redis():
    """Create mock Redis for testing."""
    return MockRedis()

def test_with_mock_redis(mock_redis):
    """Test with mock Redis."""
    # Test state operations
    mock_redis.set_state("key", "value")
    assert mock_redis.get_state("key") == "value"
    
    # Test hash operations
    mock_redis.set_hash("hash", "field", "value")
    assert mock_redis.get_hash("hash", "field") == "value"
    
    # Test template caching
    mock_redis.cache_template("template_id", {"content": "test"})
    template = mock_redis.get_cached_template("template_id")
    assert template["content"] == "test"
    
    # Test stage state
    mock_redis.set_stage_state("conv_id", "stage_id")
    stage = mock_redis.get_stage_state("conv_id")
    assert stage == "stage_id"
```

### API Testing
```python
@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_endpoint(client):
    """Test API endpoint."""
    response = client.get('/api/endpoint')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

### Template Testing
```python
def test_template_rendering():
    """Test template rendering."""
    template = TemplateManager()
    result = template.render(
        template_id="test_template",
        context={"name": "Test"}
    )
    assert "Hello Test" in result

def test_template_caching():
    """Test template caching."""
    template = TemplateManager()
    # First render should cache
    result1 = template.render("test_template", {"name": "Test"})
    # Second render should use cache
    result2 = template.render("test_template", {"name": "Test"})
    assert result1 == result2

def test_template_variables():
    """Test template variables."""
    template = TemplateManager()
    variables = template.get_variables("test_template")
    assert "name" in variables
    assert variables["name"]["type"] == "string"
```

## Coverage Requirements

### Minimum Coverage
- Overall: 80%
- Critical paths: 90%
- Core logic: 85%
- Redis operations: 90%
- Template system: 85%

### Coverage Reports
- Generate HTML reports
- Track coverage trends
- Set coverage thresholds
- Monitor critical paths
- Monitor Redis operations
- Monitor template system

## Test Data

### Fixtures
- Use pytest fixtures
- Load test data
- Clean up after tests
- Share common setup
- Mock Redis state
- Mock template cache

### Test Database
- Use separate database
- Reset between tests
- Load test data
- Clean up after tests

### Test Redis
- Use separate Redis instance
- Clear between tests
- Load test data
- Clean up after tests
- Test template caching
- Test state management

## Running Tests

### Command Line
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific tests
pytest tests/unit/message_processing/
pytest tests/unit/redis/
pytest tests/unit/template_management/

# Run with verbose output
pytest -v
```

### CI/CD Integration
- Run on every push
- Generate coverage reports
- Fail on coverage drop
- Track test results
- Monitor Redis tests
- Monitor template tests

## Best Practices

### Test Organization
- Group related tests
- Separate Redis tests
- Separate template tests
- Use appropriate fixtures
- Clean up resources
- Mock external services

### Test Isolation
- Use separate databases
- Use separate Redis instances
- Clear caches between tests
- Reset state between tests
- Mock external services
- Use appropriate timeouts

### Error Handling
- Test error conditions
- Test Redis failures
- Test template errors
- Test state transitions
- Test cache invalidation
- Test recovery mechanisms

## Related Documentation
- See `planning/code_patterns.md` for implementation patterns
- See `planning/template_system.md` for template details
- See `planning/stage_management.md` for stage management
- See `planning/message_handling_flow.md` for message flow

Last Updated: 2025-05-12
