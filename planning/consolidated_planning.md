# ICMP Events API - Documentation Overview

## System Overview
The ICMP Events API is a backend service that handles messaging integrations (WhatsApp, Facebook Messenger) with AI-powered conversation management capabilities.

## Documentation Structure

### Core Architecture
For detailed system architecture and component information, see [Architecture Documentation](architecture.md)

### API Documentation
- [API Structure and Endpoints](api_structure.md)
- [Detailed API Documentation](api_documentation.md)

### Database
- [Database Schema](database_schema.md)
- [Database Migration Guide](database_migration_guide.md)

### Testing
The testing framework is organized in the `tests/` directory with the following structure:

#### Core Test Files
- `test_api_endpoints.py` - API endpoint testing
- `test_error_handling.py` - Error handling system tests
- `test_template_system.py` - Template system tests
- `test_enhanced_extraction.py` - Data extraction tests

#### Error Handling Tests
- `test_error_integration.py` - Error handling integration tests
- `test_error_decorators.py` - Error decorator tests
- `test_error_exceptions.py` - Custom exception tests
- `test_error_utils.py` - Error utility tests
- `test_error_middleware.py` - Error middleware tests
- `test_error_config.py` - Error configuration tests
- `test_error_handling_integration.py` - Error handling integration tests
- `test_error_response.py` - Error response format tests
- `test_error_logging.py` - Error logging tests
- `test_error_validation.py` - Error validation tests
- `test_error_recovery.py` - Error recovery tests
- `test_error_monitoring.py` - Error monitoring tests
- `test_error_tracking.py` - Error tracking tests

#### Test Support Files
- `conftest.py` - Pytest configuration and fixtures
- `setup_test_database.py` - Test database setup
- `test_factories.py` - Test data factories
- `factories.py` - Factory patterns for test data

#### Test Configuration
- `tests/config/` - Test configuration files
- `tests/utils/` - Test utility functions
- `tests/migrations/` - Test database migrations

For detailed testing documentation, see:
- [Testing Strategy](testing_strategy.md)
- [Test Isolation Guidelines](test_isolation.md)
- [Test Data Seeding](test_data_seeding.md)

### Template System
For comprehensive template system documentation, see [Template System](template_system.md)

### Security
- [Authentication](authentication.md)
- [Error Handling](error_handling.md)

### Development & Deployment
- [Implementation Guide](implementation_guide.md)
- [Deployment Guide](deployment.md)
- [Environment Variables](environment_variables.md)
- [Monitoring](monitoring.md)

### Frontend
- [Frontend Guide](frontend_guide.md)

### Project Management
- [Development Roadmap](development_roadmap.md)
- [Progress Plan](progress_plan.md)
- [Project Overview](project_overview.md)

## Current Development Status

### Completed
- Basic template management system
- Database connection pooling
- Core API endpoints
- Initial error handling
- Basic testing framework
- Comprehensive error handling test suite
- API endpoint test coverage

### In Progress
- Codebase reorganization
- Template variable provider fixes
- OpenAI integration improvements
- API documentation updates
- Enhanced test coverage for new features

### Next Steps
1. Complete codebase reorganization
2. Implement comprehensive testing
3. Enhance error handling
4. Improve documentation
5. Optimize performance
6. Add monitoring
7. Implement caching
8. Enhance security measures

## Timeline
- Phase 1 (Current): 1-2 weeks
- Phase 2 (Testing): 2-3 weeks
- Phase 3 (Error Handling): 1-2 weeks
- Phase 4 (Performance): 2-3 weeks
- Phase 5 (Security): 1-2 weeks
- Phase 6 (Documentation): 1-2 weeks
- Phase 7 (Monitoring): 1-2 weeks
- Phase 8 (Features): 2-4 weeks

Total estimated time: 11-20 weeks

## Additional Resources
- [Code Patterns](code_patterns.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Message Handling Flow](message_handling_flow.md)
- [Stage Management](stage_management.md)
- [Refactor Summary](refactor_summary.md)

Last Updated: 2025-05-12
