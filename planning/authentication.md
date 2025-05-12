# Authentication System Documentation

## Overview
Our system uses API key-based authentication to secure all endpoints. This document explains how authentication works and how to implement it.

## Authentication Flow

### 1. Getting an API Key
```http
POST /api/auth/register
Content-Type: application/json

{
    "business_name": "Your Business",
    "email": "your@email.com",
    "password": "secure-password"
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "api_key": "your-api-key-here",
        "expires_at": "2024-04-11T12:00:00Z"
    }
}
```

### 2. Using the API Key
Include the API key in all requests:
```http
GET /api/endpoint
Authorization: Bearer your-api-key-here
```

### 3. Refreshing the API Key
```http
POST /api/auth/refresh
Authorization: Bearer your-api-key-here
```

Response:
```json
{
    "status": "success",
    "data": {
        "api_key": "new-api-key-here",
        "expires_at": "2024-05-11T12:00:00Z"
    }
}
```

## Security Features

### 1. API Key Format
- 32 characters minimum
- Alphanumeric with hyphens
- Example: `abc123def456-ghi789jkl012-mno345pqr678`

### 2. Access Levels
1. **Admin**
   - Full system access
   - Can manage users
   - Can manage templates
   - Can view all data

2. **User**
   - Can send messages
   - Can use templates
   - Can view own data
   - Limited system access

3. **Read-Only**
   - Can view data
   - Cannot make changes
   - Limited access

### 3. Rate Limiting
- 100 requests per minute
- 1000 requests per hour
- Headers included in response:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 99
  X-RateLimit-Reset: 1615459200
  ```

## Implementation

### 1. Python Code
```python
def validate_api_key(api_key):
    if not api_key:
        raise AuthError("API key is required")
    
    # Validate format
    if not re.match(r'^[A-Za-z0-9-_]{32,}$', api_key):
        raise AuthError("Invalid API key format")
    
    # Check in database
    if not is_valid_api_key(api_key):
        raise AuthError("Invalid API key")
    
    # Check expiration
    if is_api_key_expired(api_key):
        raise AuthError("API key has expired")
    
    # Check rate limits
    if is_rate_limit_exceeded(api_key):
        raise AuthError("Rate limit exceeded")
```

### 2. Database Schema
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    key TEXT NOT NULL,
    business_id UUID NOT NULL,
    access_level TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE rate_limits (
    api_key_id UUID PRIMARY KEY,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP NOT NULL,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
);
```

## Error Handling

### 1. Authentication Errors
```json
{
    "status": "error",
    "error": {
        "code": "AUTH_001",
        "message": "Invalid API key",
        "details": {
            "reason": "Key has expired"
        }
    }
}
```

### 2. Rate Limit Errors
```json
{
    "status": "error",
    "error": {
        "code": "RATE_001",
        "message": "Rate limit exceeded",
        "details": {
            "limit": 100,
            "remaining": 0,
            "reset": 1615459200
        }
    }
}
```

## Best Practices

1. **API Key Security**
   - Never share API keys
   - Rotate keys regularly
   - Use different keys for different environments
   - Monitor key usage

2. **Error Handling**
   - Always check for authentication errors
   - Handle rate limit errors
   - Implement retry logic
   - Log authentication failures

3. **Monitoring**
   - Track API key usage
   - Monitor rate limits
   - Log authentication attempts
   - Alert on suspicious activity

## Integration Examples

### 1. Python Requests
```python
import requests

def make_api_request(endpoint, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_api_error(e)
```

### 2. JavaScript Fetch
```javascript
async function makeApiRequest(endpoint, apiKey) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        return await response.json();
    } catch (error) {
        handleApiError(error);
    }
}
```

## Support

### 1. Common Issues
- Invalid API key format
- Expired API key
- Rate limit exceeded
- Missing authentication header

### 2. Getting Help
- Check error messages
- Review documentation
- Contact support
- Check logs

## Updates
This document will be updated as we make changes to the authentication system. Check back often for new features and security improvements.

Last Updated: 2025-05-12
