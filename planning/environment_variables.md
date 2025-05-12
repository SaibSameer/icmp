# Environment Variables Documentation

> Note: Test environment variables setup is currently in progress as part of the testing improvements. Major runtime and import errors (including get_db_connection import in tests/conftest.py) have been resolved as of 2025-05-12. Stubs for error handling (ErrorUtils, template_system) have also been added, and the test environment is ready for further development.

## Overview
This document outlines all environment variables used in the ICMP Backend service. These variables control various aspects of the application's behavior, including database connections, API configurations, and security settings.

## Database Configuration

### DB_NAME
- **Description**: Name of the PostgreSQL database
- **Type**: String
- **Default**: `icmp_db`
- **Required**: Yes
- **Example**: `DB_NAME=icmp_db`

### DB_USER
- **Description**: PostgreSQL database username
- **Type**: String
- **Default**: `postgres`
- **Required**: Yes
- **Example**: `DB_USER=postgres`

### DB_PASSWORD
- **Description**: PostgreSQL database password
- **Type**: String
- **Default**: None
- **Required**: Yes
- **Example**: `DB_PASSWORD=your_secure_password`

### DB_HOST
- **Description**: PostgreSQL database host
- **Type**: String
- **Default**: `localhost`
- **Required**: Yes
- **Example**: `DB_HOST=localhost`

### DB_PORT
- **Description**: PostgreSQL database port
- **Type**: Integer
- **Default**: `5432`
- **Required**: Yes
- **Example**: `DB_PORT=5432`

## API Configuration

### API_VERSION
- **Description**: API version number
- **Type**: String
- **Default**: `1.0.0`
- **Required**: No
- **Example**: `API_VERSION=1.0.0`

### API_RATE_LIMIT
- **Description**: Maximum number of requests per minute
- **Type**: Integer
- **Default**: `100`
- **Required**: No
- **Example**: `API_RATE_LIMIT=100`

### API_KEY_HEADER
- **Description**: Header name for API key authentication
- **Type**: String
- **Default**: `X-API-Key`
- **Required**: No
- **Example**: `API_KEY_HEADER=X-API-Key`

## Security

### JWT_SECRET
- **Description**: Secret key for JWT token generation
- **Type**: String
- **Default**: None
- **Required**: Yes
- **Example**: `JWT_SECRET=your_jwt_secret_key`

### JWT_EXPIRATION
- **Description**: JWT token expiration time in seconds
- **Type**: Integer
- **Default**: `3600`
- **Required**: No
- **Example**: `JWT_EXPIRATION=3600`

### CORS_ORIGINS
- **Description**: Allowed CORS origins
- **Type**: String (comma-separated)
- **Default**: `*`
- **Required**: No
- **Example**: `CORS_ORIGINS=http://localhost:3000,https://example.com`

## External Services

### OPENAI_API_KEY
- **Description**: OpenAI API key for AI integration
- **Type**: String
- **Default**: None
- **Required**: Yes
- **Example**: `OPENAI_API_KEY=your_openai_api_key`

### WHATSAPP_API_KEY
- **Description**: WhatsApp Business API key
- **Type**: String
- **Default**: None
- **Required**: Yes
- **Example**: `WHATSAPP_API_KEY=your_whatsapp_api_key`

### MESSENGER_API_KEY
- **Description**: Facebook Messenger API key
- **Type**: String
- **Default**: None
- **Required**: Yes
- **Example**: `MESSENGER_API_KEY=your_messenger_api_key`

## Logging

### LOG_LEVEL
- **Description**: Logging level
- **Type**: String
- **Default**: `INFO`
- **Required**: No
- **Example**: `LOG_LEVEL=INFO`

### LOG_FORMAT
- **Description**: Log message format
- **Type**: String
- **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Required**: No
- **Example**: `LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### LOG_FILE
- **Description**: Path to log file
- **Type**: String
- **Default**: `logs/app.log`
- **Required**: No
- **Example**: `LOG_FILE=logs/app.log`

## Redis Configuration

### REDIS_HOST
- **Description**: Redis server host
- **Type**: String
- **Default**: `localhost`
- **Required**: Yes
- **Example**: `REDIS_HOST=localhost`

### REDIS_PORT
- **Description**: Redis server port
- **Type**: Integer
- **Default**: `6379`
- **Required**: Yes
- **Example**: `REDIS_PORT=6379`

### REDIS_PASSWORD
- **Description**: Redis server password
- **Type**: String
- **Default**: None
- **Required**: No
- **Example**: `REDIS_PASSWORD=your_redis_password`

### REDIS_DB
- **Description**: Redis database number
- **Type**: Integer
- **Default**: `0`
- **Required**: No
- **Example**: `REDIS_DB=0`

### REDIS_SSL
- **Description**: Enable SSL for Redis connection
- **Type**: Boolean
- **Default**: `false`
- **Required**: No
- **Example**: `REDIS_SSL=true`

### REDIS_MAX_CONNECTIONS
- **Description**: Maximum number of Redis connections in pool
- **Type**: Integer
- **Default**: `10`
- **Required**: No
- **Example**: `REDIS_MAX_CONNECTIONS=10`

### REDIS_SOCKET_TIMEOUT
- **Description**: Redis socket timeout in seconds
- **Type**: Integer
- **Default**: `5`
- **Required**: No
- **Example**: `REDIS_SOCKET_TIMEOUT=5`

### REDIS_RETRY_ON_TIMEOUT
- **Description**: Retry Redis operations on timeout
- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Example**: `REDIS_RETRY_ON_TIMEOUT=true`

### REDIS_HEALTH_CHECK_INTERVAL
- **Description**: Redis health check interval in seconds
- **Type**: Integer
- **Default**: `30`
- **Required**: No
- **Example**: `REDIS_HEALTH_CHECK_INTERVAL=30`

## Template Management

---

**Update 2025-05-12:**
- Main environment variable documentation is up to date.
- Test environment variable setup is ongoing, but all critical runtime/import issues are resolved.


### TEMPLATE_CACHE_TTL
- **Description**: Template cache time-to-live in seconds
- **Type**: Integer
- **Default**: `3600`
- **Required**: No
- **Example**: `TEMPLATE_CACHE_TTL=3600`

### TEMPLATE_VALIDATION_STRICT
- **Description**: Enable strict template validation
- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Example**: `TEMPLATE_VALIDATION_STRICT=true`

## Development

### FLASK_ENV
- **Description**: Flask environment
- **Type**: String
- **Default**: `development`
- **Required**: No
- **Example**: `FLASK_ENV=development`

### DEBUG
- **Description**: Enable debug mode
- **Type**: Boolean
- **Default**: `false`
- **Required**: No
- **Example**: `DEBUG=true`

### TESTING
- **Description**: Enable testing mode
- **Type**: Boolean
- **Default**: `false`
- **Required**: No
- **Example**: `TESTING=true`

## Environment Setup

### Development Environment
```bash
# Database
DB_NAME=icmp_db
DB_USER=postgres
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

# API
API_VERSION=1.0.0
API_RATE_LIMIT=100
API_KEY_HEADER=X-API-Key

# Security
JWT_SECRET=dev_jwt_secret
JWT_EXPIRATION=3600
CORS_ORIGINS=http://localhost:3000

# External Services
OPENAI_API_KEY=your_openai_api_key
WHATSAPP_API_KEY=your_whatsapp_api_key
MESSENGER_API_KEY=your_messenger_api_key

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=logs/app.log

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SSL=false
REDIS_MAX_CONNECTIONS=10
REDIS_SOCKET_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
REDIS_HEALTH_CHECK_INTERVAL=30

# Template Management
TEMPLATE_CACHE_TTL=3600
TEMPLATE_VALIDATION_STRICT=true

# Development
FLASK_ENV=development
DEBUG=true
TESTING=false
```

### Production Environment
```bash
# Database
DB_NAME=icmp_db
DB_USER=prod_user
DB_PASSWORD=prod_secure_password
DB_HOST=prod-db.example.com
DB_PORT=5432

# API
API_VERSION=1.0.0
API_RATE_LIMIT=1000
API_KEY_HEADER=X-API-Key

# Security
JWT_SECRET=prod_jwt_secret
JWT_EXPIRATION=3600
CORS_ORIGINS=https://app.example.com

# External Services
OPENAI_API_KEY=prod_openai_api_key
WHATSAPP_API_KEY=prod_whatsapp_api_key
MESSENGER_API_KEY=prod_messenger_api_key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=/var/log/icmp/app.log

# Redis
REDIS_HOST=prod-redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=prod_redis_password
REDIS_DB=0
REDIS_SSL=true
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
REDIS_HEALTH_CHECK_INTERVAL=30

# Template Management
TEMPLATE_CACHE_TTL=3600
TEMPLATE_VALIDATION_STRICT=true

# Development
FLASK_ENV=production
DEBUG=false
TESTING=false
```

## Related Documentation
- See `planning/code_patterns.md` for implementation patterns
- See `planning/testing_strategy.md` for testing guidelines
- See `planning/deployment.md` for deployment instructions

Last Updated: 2025-05-12

---
**Update:**
- The get_db_connection import error in tests/conftest.py was fixed by updating the import to backend.database.db.
- New error handling stubs (ErrorConfig, ErrorMonitor, ErrorLogger, ErrorResponse, ErrorValidator, ErrorRecovery) were added to backend/error_handling/errors.py for test compatibility on 2025-05-12.

