# Code Patterns and Syntax Guide

## Import Structure

### General Rules
1. Use relative imports (`.`, `..`) for imports within the same package
2. Use absolute imports (`backend.`) for imports from different packages
3. Group imports by type (core, services, database, local)
4. Avoid circular dependencies by using late imports when necessary

### Example Structure
```python
# Standard library imports
import logging
import uuid
from typing import Dict, Any

# Core imports
from ..core.errors import ValidationError

# Service imports
from .services.llm_service import LLMService

# Database imports
from ..db.connection_manager import ConnectionManager
from backend.config import get_db_config  # Database configuration

# Redis imports
from backend.redis.redis_state_manager import RedisStateManager
from backend.config import Config  # Redis configuration

# AI imports
from backend.ai.openai_helper import call_openai

# Template imports
from backend.template_management import TemplateManager
from backend.message_processing.template_variables import TemplateVariableProvider

# Local imports
from .template_variables import TemplateVariableProvider
```

## Database Operations

### Connection Management
```python
# Get connection from pool
conn = get_db_connection()
try:
    # Database operations
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
finally:
    release_db_connection(conn)
```

## Query Execution
```python
# Parameterized query
query = """
    SELECT * FROM table 
    WHERE column = %s 
    AND status = %s
"""
params = (value, status)
result = execute_query(query, params)
```

## Transaction Management
```python
# Transaction with context manager
with get_db_transaction() as conn:
    # Multiple operations
    execute_query(conn, query1, params1)
    execute_query(conn, query2, params2)
    # Transaction automatically commits or rolls back
```

## Redis Operations

### State Management
```python
# Initialize Redis manager
redis_manager = RedisStateManager(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    password=Config.REDIS_PASSWORD,
    ssl=Config.REDIS_SSL
)

# Set state
redis_manager.set_state("key", value)

# Get state
value = redis_manager.get_state("key")

# Delete state
redis_manager.delete_state("key")
```

### Hash Operations
```python
# Set hash field
redis_manager.set_hash("hash_key", "field", value)

# Get hash field
value = redis_manager.get_hash("hash_key", "field")

# Delete hash field
redis_manager.delete_hash("hash_key", "field")
```

### Error Handling
```python
try:
    # Redis operations
    redis_manager.set_state("key", value)
except Exception as e:
    logger.error(f"Redis error: {str(e)}")
    # Implement fallback or retry logic
```

## Error Handling

### Standard Error Pattern
```python
try:
    # Operation
    result = perform_operation()
except SpecificError as e:
    logger.error(f"Error in operation: {str(e)}", exc_info=True)
    raise CustomError("User-friendly message") from e
```

### API Error Response
```python
@app.errorhandler(CustomError)
def handle_error(error):
    return jsonify({
        "status": "error",
        "error": {
            "code": error.code,
            "message": str(error),
            "details": error.details
        }
    }), error.status_code
```

## API Response Format

### Success Response
```python
def success_response(data=None, message="Success"):
    return jsonify({
        "status": "success",
        "data": data,
        "message": message
    }), 200
```

### Error Response
```python
def error_response(code, message, details=None, status_code=400):
    return jsonify({
        "status": "error",
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }), status_code
```

## Message Processing

### WhatsApp Message Handling
```python
def handle_whatsapp_message(message):
    # Extract message data
    sender_id = message["from"]
    message_text = message["text"]["body"]
    
    # Process message
    response = process_message(sender_id, message_text)
    
    # Send response
    send_whatsapp_message(sender_id, response)
```

### Messenger Message Handling
```python
def handle_messenger_message(message):
    # Extract message data
    sender_id = message["sender"]["id"]
    message_text = message["message"]["text"]
    
    # Process message
    response = process_message(sender_id, message_text)
    
    # Send response
    send_messenger_message(sender_id, response)
```

## Template Management

### Template Creation and Usage
```python
# Initialize template manager
template_manager = TemplateManager()

# Get template details
template = template_manager.get_template(template_id)

# Render template with context
context = {
    'user_name': 'John',
    'business_name': 'Acme Corp'
}
rendered_content = template_manager.render(template_id, context)
```

## Template Variable Registration
```python
# Register a variable provider with metadata
@TemplateVariableProvider.register_provider(
    'my_variable',
    description="Provides a custom variable value",
    auth_requirement='business_key',
    validation_rules={
        'type': 'string',
        'min_length': 1,
        'max_length': 100
    },
    cache_ttl=300  # Cache for 5 minutes
)
def provide_my_variable(context):
    """Provide custom variable value."""
    return "Variable value"

# Register a standard variable provider
@TemplateVariableProvider.register_provider(
    'timestamp',
    description="Provides current timestamp",
    cache_ttl=60  # Cache for 1 minute
)
def timestamp_provider(context):
    """Provide current timestamp."""
    return context['timestamp'].isoformat()

# Register a variable with Redis caching
@TemplateVariableProvider.register_provider(
    'cached_variable',
    description="Provides cached variable value",
    cache_ttl=3600,  # Cache for 1 hour
    use_redis=True
)
def cached_variable_provider(context):
    """Provide cached variable value."""
    redis_key = f"var:cached_variable:{context['id']}"
    cached_value = redis_manager.get_state(redis_key)
    if cached_value:
        return cached_value
    
    value = compute_expensive_value(context)
    redis_manager.set_state(redis_key, value)
    return value
```

## AI Integration

### OpenAI API Call
```python
def get_ai_response(prompt, context=None):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise AIError("Failed to get AI response") from e
```

## Configuration Management

### Environment Variables
```python
# Load environment variables
load_dotenv()

# Access configuration
config = {
    "database_url": os.getenv("DATABASE_URL"),
    "api_key": os.getenv("API_KEY"),
    "openai_key": os.getenv("OPENAI_API_KEY"),
    "redis_host": os.getenv("REDIS_HOST", "localhost"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "redis_db": int(os.getenv("REDIS_DB", 0)),
    "redis_password": os.getenv("REDIS_PASSWORD"),
    "redis_ssl": os.getenv("REDIS_SSL", "false").lower() == "true"
}
```

## Configuration Validation
```python
def validate_config(config):
    required_keys = [
        "database_url",
        "api_key",
        "openai_key",
        "redis_host",
        "redis_port"
    ]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ConfigError(f"Missing required configuration: {missing_keys}")
```

## Logging

### Standard Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Redis Logging
```python
# Log Redis operations
logger.info(f"Setting Redis state: {key}")
try:
    redis_manager.set_state(key, value)
    logger.info(f"Successfully set Redis state: {key}")
except Exception as e:
    logger.error(f"Failed to set Redis state: {key}, error: {str(e)}")
    raise
```

## Testing

### Unit Tests
```python
def test_template_variable():
    # Setup
    provider = TemplateVariableProvider()
    
    # Test registration
    @provider.register_provider('test_var')
    def test_var(context):
        return "test value"
    
    # Test retrieval
    value = provider.get_variable('test_var', {})
    assert value == "test value"
```

### Integration Tests
```python
def test_redis_integration():
    # Setup
    redis_manager = RedisStateManager(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT
    )
    
    # Test state operations
    redis_manager.set_state("test_key", "test_value")
    value = redis_manager.get_state("test_key")
    assert value == "test_value"
    
    # Cleanup
    redis_manager.delete_state("test_key")
```

### Mock Redis for Testing
```python
class MockRedis:
    def __init__(self):
        self.store = {}
    
    def set_state(self, key, value):
        self.store[key] = value
    
    def get_state(self, key):
        return self.store.get(key)
    
    def delete_state(self, key):
        if key in self.store:
            del self.store[key]

# Use in tests
redis_manager = MockRedis()
```

## Performance Optimization

### Caching Strategy
```python
# Cache template
def get_template(template_id):
    cache_key = f"template:{template_id}"
    cached = redis_manager.get_state(cache_key)
    if cached:
        return cached
    
    template = fetch_template_from_db(template_id)
    redis_manager.set_state(cache_key, template)
    return template

# Cache variable values
def get_variable_value(variable_name, context):
    cache_key = f"var:{variable_name}:{context['id']}"
    cached = redis_manager.get_state(cache_key)
    if cached:
        return cached
    
    value = compute_variable_value(variable_name, context)
    redis_manager.set_state(cache_key, value)
    return value
```

### Connection Pooling
```python
# Database connection pool
db_pool = get_db_pool()

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB
)
```

## Security

### Redis Security
```python
# Secure Redis connection
redis_manager = RedisStateManager(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASSWORD,
    ssl=Config.REDIS_SSL
)

# Encrypt sensitive data
def store_sensitive_data(key, data):
    encrypted_data = encrypt_data(data)
    redis_manager.set_state(key, encrypted_data)

def get_sensitive_data(key):
    encrypted_data = redis_manager.get_state(key)
    return decrypt_data(encrypted_data)
```

Last Updated: 2025-05-12
