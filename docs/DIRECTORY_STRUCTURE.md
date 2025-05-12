# New Directory Structure

## Overview
This document outlines the new directory structure for the system after cleanup and reorganization.

## Directory Structure

```
backend/
├── core/                    # Core functionality
│   ├── message_processing/  # Message handling
│   │   ├── __init__.py
│   │   ├── handler.py
│   │   ├── processor.py
│   │   └── validator.py
│   ├── templates/          # Template management
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   ├── variables.py
│   │   └── validator.py
│   └── stages/            # Stage management
│       ├── __init__.py
│       ├── manager.py
│       └── validator.py
├── services/               # All services
│   ├── __init__.py
│   ├── ai/                # AI services
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   └── controller.py
│   ├── messaging/         # Messaging services
│   │   ├── __init__.py
│   │   └── handler.py
│   └── monitoring/        # Monitoring services
│       ├── __init__.py
│       └── health.py
├── database/              # Database management
│   ├── __init__.py
│   ├── config.py
│   ├── connection.py
│   ├── migrations/        # Database migrations
│   │   └── versions/
│   └── models/           # Database models
│       ├── __init__.py
│       └── base.py
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── routes/
│   └── schemas/
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── general.py
│   ├── database.py
│   └── validation.py
└── tests/                 # Tests
    ├── __init__.py
    ├── unit/
    ├── integration/
    └── e2e/

docs/                      # Documentation
├── architecture/          # Architecture documentation
│   ├── overview.md
│   ├── components.md
│   └── data_flow.md
├── api/                   # API documentation
│   ├── endpoints.md
│   └── schemas.md
├── development/          # Development documentation
│   ├── setup.md
│   ├── guidelines.md
│   └── best_practices.md
└── deployment/           # Deployment documentation
    ├── installation.md
    └── configuration.md
```

## Directory Purposes

### Core Components
- **message_processing/**: Handles all message-related functionality
- **templates/**: Manages template system and variables
- **stages/**: Handles conversation stage management

### Services
- **ai/**: AI and LLM integration services
- **messaging/**: Message handling services
- **monitoring/**: System monitoring and health checks

### Database
- **migrations/**: Database migration files
- **models/**: Database models and schemas

### API
- **routes/**: API endpoint definitions
- **schemas/**: API request/response schemas

### Utilities
- **general.py**: General utility functions
- **database.py**: Database utility functions
- **validation.py**: Validation utility functions

### Tests
- **unit/**: Unit tests
- **integration/**: Integration tests
- **e2e/**: End-to-end tests

### Documentation
- **architecture/**: System architecture documentation
- **api/**: API documentation
- **development/**: Development guidelines
- **deployment/**: Deployment instructions

## File Naming Conventions

1. **Python Files**
   - Use snake_case
   - Descriptive names
   - Clear purpose indication

2. **Configuration Files**
   - Use lowercase
   - Clear purpose indication
   - Consistent naming

3. **Test Files**
   - Prefix with 'test_'
   - Match tested file name
   - Clear test purpose

4. **Documentation Files**
   - Use lowercase
   - Descriptive names
   - Markdown format

## Best Practices

1. **File Organization**
   - Keep related files together
   - Clear directory structure
   - Consistent naming

2. **Code Organization**
   - Single responsibility principle
   - Clear module boundaries
   - Proper encapsulation

3. **Documentation**
   - Keep documentation updated
   - Clear file purposes
   - Usage examples

4. **Testing**
   - Comprehensive test coverage
   - Clear test organization
   - Proper test naming 