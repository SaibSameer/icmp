# ICMP Events API Structure Documentation

## Directory Structure

```
backend/
├── api/                    # API versioning and endpoints
├── routes/                 # Route definitions (obsolete test files deleted May 2025)
├── services/              # Business logic services
├── message_processing/    # Message handling logic
├── database/             # Database related code
├── schemas/              # API schemas and validation
├── migrations/           # Database migrations
├── db/                   # Database utilities
├── templates/            # Template management
├── monitoring/           # Monitoring and logging
├── utils/                # Utility functions
│   ├── response_handler.py    # Standardized response handling
│   ├── error_handler.py       # Error handling and logging
│   └── request_validator.py   # Request validation utilities
├── ai/                   # AI and LLM related code
├── tests/                # Test files (obsolete test files deleted May 2025)
└── documentation/        # Documentation files
```

## API Endpoints

### Core Endpoints
- `/` - Home route
- `/ping` - Health check
- `/health` - Detailed health status
- `/api/admin-check` - Admin key validation

### Authentication & Authorization
- `/api/auth/*` - Authentication endpoints
- `/api/save-config` - Save user/business configuration
- `/api/lookup-owner` - Business owner lookup
- `/api/verify-owner` - Owner verification

### Business Management
- `/api/businesses/*` - Business CRUD operations
- `/api/config/*` - Configuration management
- `/api/users/*` - User management

### Message Handling
- `/api/messages/*` - Message processing
- `/api/routing/*` - Message routing
- `/api/conversations/*` - Conversation management
- `/api/simulate/*` - Message simulation

### Template Management
- `/api/templates/*` - Template CRUD
- `/api/template-admin/*` - Template administration
- `/api/template-variables/*` - Template variables
- `/api/template-test/*` - Template testing

### AI & LLM
- `/api/llm/*` - LLM operations
- `/api/data-extraction/*` - Data extraction
- `/api/agents/*` - Agent management

### Other Services
- `/api/stages/*` - Stage management
- `/api/privacy/*` - Privacy controls
- `/api/user-stats/*` - User statistics

## Response Format

### Success Response
```json
{
    "status": "success",
    "data": {},
    "message": "Success message",
    "metadata": {
        "timestamp": "ISO8601",
        "version": "1.0"
    }
}
```

### Error Response
```json
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {} // Optional
    },
    "metadata": {
        "timestamp": "ISO8601",
        "version": "1.0"
    }
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| VALIDATION_ERROR | Input validation failed | 400 |
| UNAUTHORIZED | Authentication required | 401 |
| FORBIDDEN | Insufficient permissions | 403 |
| NOT_FOUND | Resource not found | 404 |
| DATABASE_ERROR | Database operation failed | 500 |
| INTERNAL_ERROR | Unexpected server error | 500 |

## Request Validation

The `RequestValidator` utility provides comprehensive request validation:

### Validation Types
1. Required Fields
```python
RequestValidator.validate_required(data, ['field1', 'field2'])
```

2. Type Validation
```python
RequestValidator.validate_types(data, {
    'name': str,
    'age': int
})
```

3. Value Validation
```python
RequestValidator.validate_values(data, {
    'status': ['active', 'inactive']
})
```

4. Length Validation
```python
RequestValidator.validate_length(data, {
    'name': {'min': 2, 'max': 50}
})
```

5. Numeric Range Validation
```python
RequestValidator.validate_numeric_range(data, {
    'age': {'min': 0, 'max': 120}
})
```

6. Pattern Validation
```python
RequestValidator.validate_pattern(data, {
    'id': r'^[a-zA-Z0-9-]+$'
})
```

### Combined Validation
```python
RequestValidator.validate_all(
    data=data,
    required_fields=['name', 'age'],
    type_map={'name': str, 'age': int},
    length_map={'name': {'min': 2, 'max': 50}},
    range_map={'age': {'min': 0, 'max': 120}}
)
```

## Implementation Example

```python
@bp.route('/example', methods=['POST'])
@handle_api_errors
def example_endpoint():
    # Get request data
    data = request.get_json()
    
    # Validate request data
    RequestValidator.validate_all(
        data=data,
        required_fields=['name', 'age'],
        type_map={'name': str, 'age': int},
        length_map={'name': {'min': 2, 'max': 50}},
        range_map={'age': {'min': 0, 'max': 120}}
    )
    
    # Process request
    result = {
        'message': f"Hello, {data['name']}!",
        'age': data['age']
    }
    
    # Return standardized response
    return APIResponse.success(
        data=result,
        message="Request processed successfully"
    )
```

## Error Handling

The `handle_api_errors` decorator provides consistent error handling:

1. Logs errors with request details
2. Handles specific error types
3. Returns standardized error responses
4. Includes stack traces in development

## Related Documentation
- See `planning/api_documentation.md` for detailed API endpoint documentation
- See `planning/database_schema.md` for database structure
- See `planning/code_patterns.md` for implementation patterns

Last Updated: 2025-05-12
