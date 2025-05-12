# API Documentation

## Base URL
```
https://api.example.com/v1
```

## Authentication
All API requests require an API key to be passed in the `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

### Authentication Methods
1. **Master API Key (`ICMP_API_KEY`)**
   - Required for administrative tasks
   - Passed via `Authorization: Bearer <ICMP_API_KEY>`
   - Used with `@require_api_key` decorator

2. **Business API Key (`businessApiKey`)**
   - Required for business-specific operations
   - Passed via `businessApiKey` HttpOnly cookie
   - Used with `@require_business_api_key` decorator

## Implementation Details
- Authentication decorators are implemented in `backend/auth.py`
- API key validation is handled by middleware
- Session management uses secure HttpOnly cookies
- Rate limiting is implemented at the route level

## Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-03-11T15:50:00Z",
    "version": "1.0.0"
}
```

### Configuration & Health
- `GET /` - Welcome message
- `POST /api/save-config` - Validates and sets business API key
- `POST /validate_config` - Validates full config details
- `GET /health` - Health check endpoint
- `GET /ping` - Simple ping endpoint

### Business Management
- `POST /businesses` - Create new business
- `GET /businesses/{business_id}` - Get business details

### Stage Management
- `POST /stages` - Create new stage with templates
- `GET /stages` - Get stages for business

### Template Management
- `POST /templates` - Create global default template
- `GET /templates` - Get all global templates

### Message Handling
- `POST /message` - Handle incoming user messages
- `GET /conversations/{user_id}` - Get user conversations

## Implementation Notes
- All endpoints are implemented in `backend/routes/`
- Request validation uses JSON schemas in `backend/schemas/`
- Error handling is standardized across all endpoints
- Response formats are consistent

## Error Handling

### Error Response Format
All error responses follow this standard format:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "field_errors": {
                "field_name": "Error message"
            },
            "context": "Additional error context"
        }
    }
}
```

### Error Codes

#### Validation Errors (400)
- `VALIDATION_ERROR`: Input validation failed
  ```json
  {
      "error": {
          "code": "VALIDATION_ERROR",
          "message": "Invalid input data",
          "details": {
              "field_errors": {
                  "email": "Invalid email format",
                  "password": "Password too short"
              }
          }
      }
  }
  ```

#### Authentication Errors (401)
- `AUTHENTICATION_ERROR`: Authentication failed
  ```json
  {
      "error": {
          "code": "AUTHENTICATION_ERROR",
          "message": "Invalid authentication token",
          "details": {
              "context": "Token expired"
          }
      }
  }
  ```

#### Authorization Errors (403)
- `AUTHORIZATION_ERROR`: Permission denied
  ```json
  {
      "error": {
          "code": "AUTHORIZATION_ERROR",
          "message": "Insufficient permissions",
          "details": {
              "required_role": "admin",
              "current_role": "user"
          }
      }
  }
  ```

#### Not Found Errors (404)
- `NOT_FOUND`: Resource not found
  ```json
  {
      "error": {
          "code": "NOT_FOUND",
          "message": "Resource not found",
          "details": {
              "resource_type": "user",
              "resource_id": "123"
          }
      }
  }
  ```

#### Database Errors (500)
- `DATABASE_ERROR`: Database operation failed
  ```json
  {
      "error": {
          "code": "DATABASE_ERROR",
          "message": "Database operation failed",
          "details": {
              "operation": "insert",
              "table": "users"
          }
      }
  }
  ```

#### Service Errors (500)
- `SERVICE_ERROR`: External service error
  ```json
  {
      "error": {
          "code": "SERVICE_ERROR",
          "message": "External service failed",
          "details": {
              "service": "payment_gateway",
              "error": "Connection timeout"
          }
      }
  }
  ```

#### Internal Errors (500)
- `INTERNAL_ERROR`: Unexpected system error
  ```json
  {
      "error": {
          "code": "INTERNAL_ERROR",
          "message": "An unexpected error occurred",
          "details": {
              "error_id": "abc123"
          }
      }
  }
  ```

### Error Handling Examples

#### 1. Validation Error
```python
from backend.error_handling import ValidationError

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'email' not in data:
        raise ValidationError(
            "Missing required fields",
            field_errors={"email": "Email is required"}
        )
```

#### 2. Authentication Error
```python
from backend.error_handling import AuthenticationError

@app.route('/api/protected', methods=['GET'])
def protected_route():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationError("Missing authentication token")
```

#### 3. Authorization Error
```python
from backend.error_handling import AuthorizationError

@app.route('/api/admin', methods=['GET'])
def admin_route():
    if not current_user.is_admin:
        raise AuthorizationError(
            "Admin access required",
            details={"required_role": "admin"}
        )
```

#### 4. Not Found Error
```python
from backend.error_handling import NotFoundError

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user(user_id)
    if not user:
        raise NotFoundError(
            "User not found",
            details={"user_id": user_id}
        )
```

#### 5. Database Error
```python
from backend.error_handling import DatabaseError

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user = db.create_user(request.json)
    except Exception as e:
        raise DatabaseError(
            "Failed to create user",
            details={"operation": "create", "table": "users"}
        )
```

#### 6. Service Error
```python
from backend.error_handling import ServiceError

@app.route('/api/payment', methods=['POST'])
def process_payment():
    try:
        result = payment_gateway.process(request.json)
    except Exception as e:
        raise ServiceError(
            "Payment processing failed",
            service_name="payment_gateway",
            details={"error": str(e)}
        )
```

## Rate Limiting
- Default: 100 requests per minute
- Configurable per endpoint
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Security
- All endpoints use HTTPS
- API keys are validated on every request
- Input is sanitized and validated
- Output is properly escaped
- CORS is properly configured

## Testing
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- API tests in `tests/api/`
- Test coverage target: > 80%

## Monitoring
- Health checks every 30 seconds
- Error tracking and logging
- Performance metrics collection
- Alert system for critical issues

## Related Documentation
- See `planning/architecture.md` for system architecture
- See `planning/database_schema.md` for database structure
- See `planning/code_patterns.md` for implementation patterns

## Admin Check
```
GET /admin/check
```
Verifies admin access and returns admin status.

**Response:**
```json
{
    "is_admin": true,
    "permissions": ["read", "write", "admin"]
}
```

### Configuration Management

#### Get Configuration
```
GET /config
```
Retrieves the current configuration.

**Response:**
```json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "icmp_db"
    },
    "api": {
        "version": "1.0.0",
        "rate_limit": 100
    }
}
```

#### Update Configuration
```
PUT /config
```
Updates the configuration.

**Request Body:**
```json
{
    "database": {
        "host": "new-host",
        "port": 5432
    }
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Configuration updated successfully"
}
```

### Message Processing

#### WhatsApp Webhook
```
POST /webhook/whatsapp
```
Handles incoming WhatsApp messages.

**Request Body:**
```json
{
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "123456789",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "1234567890",
                    "phone_number_id": "987654321"
                },
                "contacts": [{
                    "profile": {
                        "name": "John Doe"
                    },
                    "wa_id": "1234567890"
                }],
                "messages": [{
                    "from": "1234567890",
                    "id": "wamid.123",
                    "timestamp": "1234567890",
                    "text": {
                        "body": "Hello"
                    },
                    "type": "text"
                }]
            }
        }]
    }]
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Webhook processed successfully"
}
```

#### Messenger Webhook
```
POST /webhook/messenger
```
Handles incoming Facebook Messenger messages.

**Request Body:**
```json
{
    "object": "page",
    "entry": [{
        "id": "123456789",
        "time": 1234567890,
        "messaging": [{
            "sender": {
                "id": "123456789"
            },
            "recipient": {
                "id": "987654321"
            },
            "timestamp": 1234567890,
            "message": {
                "mid": "m_123",
                "text": "Hello"
            }
        }]
    }]
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Webhook processed successfully"
}
```

### Template Management

#### Create Template
```
POST /templates
```
Creates a new template.

**Request Body:**
```json
{
    "business_id": "uuid",
    "template_name": "string",
    "template_type": "string",
    "content": "string",
    "system_prompt": "string",
    "is_default": false
}
```

**Response:**
```json
{
    "template_id": "uuid",
    "business_id": "uuid",
    "template_name": "string",
    "template_type": "string",
    "content": "string",
    "system_prompt": "string",
    "is_default": false,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### Get Template
```
GET /templates/{template_id}
```
Retrieves a specific template.

**Response:**
```json
{
    "template_id": "uuid",
    "business_id": "uuid",
    "template_name": "string",
    "template_type": "string",
    "content": "string",
    "system_prompt": "string",
    "is_default": false,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### List Templates
```
GET /templates
```
Lists all templates for a business.

**Query Parameters:**
- `business_id` (required): UUID of the business
- `template_type` (optional): Filter by template type
- `is_default` (optional): Filter by default status

**Response:**
```json
{
    "templates": [
        {
            "template_id": "uuid",
            "business_id": "uuid",
            "template_name": "string",
            "template_type": "string",
            "content": "string",
            "system_prompt": "string",
            "is_default": false,
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
}
```

#### Update Template
```
PUT /templates/{template_id}
```
Updates an existing template.

**Request Body:**
```json
{
    "template_name": "string",
    "template_type": "string",
    "content": "string",
    "system_prompt": "string",
    "is_default": false
}
```

**Response:**
```json
{
    "template_id": "uuid",
    "business_id": "uuid",
    "template_name": "string",
    "template_type": "string",
    "content": "string",
    "system_prompt": "string",
    "is_default": false,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### Delete Template
```
DELETE /templates/{template_id}
```
Deletes a template.

**Response:**
```json
{
    "status": "success",
    "message": "Template deleted successfully"
}
```

#### Render Template
```
POST /templates/{template_id}/render
```
Renders a template with provided variables.

**Request Body:**
```json
{
    "variables": {
        "key1": "value1",
        "key2": "value2"
    }
}
```

**Response:**
```json
{
    "rendered_content": "string",
    "variables_used": ["key1", "key2"]
}
```

#### List Available Variables
```
GET /templates/{template_id}/variables
```
Lists all available variables for a template.

**Response:**
```json
{
    "variables": [
        {
            "name": "string",
            "description": "string",
            "required": true,
            "default_value": "string"
        }
    ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "Bad Request",
    "message": "Invalid request parameters",
    "details": {
        "field": "name",
        "error": "Field is required"
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Unauthorized",
    "message": "Invalid or missing API key"
}
```

### 403 Forbidden
```json
{
    "error": "Forbidden",
    "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
    "error": "Not Found",
    "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
    "error": "Too Many Requests",
    "message": "Rate limit exceeded",
    "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal Server Error",
    "message": "An unexpected error occurred"
}
```

Last Updated: 2025-05-12
