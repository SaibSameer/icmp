# Project File Structure

This document provides a comprehensive overview of the project's file structure and the purpose of each file and directory.

## Root Directory Structure

### Core Directories
- `backend/` - Main backend application code
- `front-end/` - React frontend application
- `tests/` - Test suite and test utilities
- `planning/` - Project documentation and planning
- `docs/` - Additional documentation
- `scripts/` - Utility scripts
- `migrations/` - Database migration files
- `templates/` - Template files
- `static/` - Static assets
- `logs/` - Application logs
- `uploads/` - File upload directory
- `temp/` - Temporary files
- `archive/` - Archived files
- `archive_output/` - Archive output directory
- `WEBSITE/` - Website related files
- `components/` - Shared components
- `venv/` - Python virtual environment
- `.ebextensions/` - Elastic Beanstalk configuration
- `.pytest_cache/` - Pytest cache directory
- `__pycache__/` - Python cache directory

### Configuration Files
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `setup.py` - Package setup script
- `setup_test_env.ps1` - PowerShell test environment setup
- `setup_test_env.bat` - Batch test environment setup
- `render.yaml` - Render deployment configuration
- `.gitignore` - Git ignore rules
- `.ebignore` - Elastic Beanstalk ignore rules
- `Procfile` - Process file for deployment
- `1.9.5` - Version file

### Database Files
- `database_setup.sql` - Database initialization script
- `create_llm_calls_table.sql` - LLM calls table creation
- `setup_database.py` - Database setup script
- `setup_local_database.py` - Local database setup
- `create_data_extraction_template.py` - Data extraction template creation

### Deployment Files
- `deploy.py` - Deployment script
- `deploy.sh` - Shell deployment script
- `deploy.bat` - Batch deployment script
- `build.sh` - Build script
- `create_eb_package.ps1` - Elastic Beanstalk package creation
- `check_deployment.py` - Deployment verification

### Test Files
- `test_conversation_history.py` - Conversation history tests
- `test_backend_connection.py` - Backend connection tests
- `serve_test.py` - Test server
- `serve_html.py` - HTML test server

### Utility Scripts
- `run.py` - Main application runner
- `run_local.py` - Local development runner
- `run_production_migration.py` - Production database migration
- `llm_debugger.py` - LLM debugging utility
- `install.py` - Installation script
- `delete_all.py` - Data cleanup script
- `clean_templates.py` - Template cleanup script
- `archiver.py` - Archive utility
- `restore.py` - Restore utility
- `a-files.py` - File management utility
- `application.py` - Application configuration

### Documentation Files
- `final-guide-to-update-message-handling.md` - Message handling guide
- `message_handling.html` - Message handling documentation
- `message_handling_render.html` - Message handling render documentation
- `variable_test.html` - Variable testing documentation
- `variables.html` - Variables documentation
- `llm.html` - LLM documentation
- `llm_debugger.html` - LLM debugger documentation
- `llm_calls.html` - LLM calls documentation
- `stages.html` - Stages documentation
- `templates.html` - Templates documentation
- `file_list.txt` - File listing

### Archive Files
- `backend.zip` - Backend archive
- `MESSAGE_HANDLING_IMPLEMENTATION.zip` - Message handling implementation archive
- `restore.zip` - Restore archive
- `combined_output (2).zip` - Combined output archive
- `archiver.zip` - Archiver utility archive
- `archive_output (2).zip` - Archive output

### Temporary Files
- `client.set_cookie('localhost'` - Temporary cookie file
- `raise` - Temporary file
- `with` - Temporary file
- `}` - Temporary file
- `assert` - Temporary file
- `domain` - Temporary file
- `client.set_cookie('businessApiKey'` - Temporary cookie file
- `client.set_cookie('icmpApiKey'` - Temporary cookie file
- `key` - Temporary file
- `flask` - Temporary file
- `curl` - Temporary file
- `cd` - Temporary file

## Backend Structure (`backend/`)
### Core Files
- `app.py` - Main application file
- `routes.py` - Route definitions
- `config.py` - Configuration settings
- `auth.py` - Authentication system
- `__init__.py` - Package initialization
- `run.py` - Application runner
- `conftest.py` - Test configuration
- `package.json` - Node.js dependencies
- `package-lock.json` - Node.js dependency lock
- `README.md` - Backend documentation
- `BACKEND_ANALYSIS.md.new` - Backend analysis document

### Core Directories
- `routes/` - API route handlers
- `models/` - Database models
- `schemas/` - JSON schemas
- `utils/` - Utility functions
- `error_handling/` - Error handling system
- `template_management/` - Template system
- `ai/` - AI integration
- `message_processing/` - Message handling
- `database/` - Database management
- `tests/` - Backend tests
- `tools/` - Development tools
- `storage/` - File storage
- `services/` - Business services
- `core/` - Core functionality
- `migrations/` - Database migrations
- `api/` - API definitions
- `db/` - Database utilities
- `templates/` - Template files
- `monitoring/` - System monitoring
- `update_services/` - Service updates
- `__pycache__/` - Python cache
- `.pytest_cache/` - Pytest cache

### Error Handling (`backend/error_handling/`)
- `errors.py` - Error definitions
- `__init__.py` - Package initialization
- `tracking.py` - Error tracking
- `middleware.py` - Error middleware

### Template Management (`backend/template_management/`)
- `__init__.py` - Package initialization
- `template_manager.py` - Template management
- `create_default_stage.py` - Default stage creation
- `add_template_type_column.py` - Template type column addition
- `update_templates.py` - Template updates
- `update_template_types.py` - Template type updates
- `add_template_type.py` - Template type addition
- `__pycache__/` - Python cache

### AI Integration (`backend/ai/`)
- `__init__.py` - Package initialization
- `openai_helper.py` - OpenAI integration helper
- `llm_service.py` - Language model service
- `__pycache__/` - Python cache

### Message Processing (`backend/message_processing/`)
#### Core Files
- `message_handler.py` - Main message handling logic
- `messenger.py` - Message delivery system
- `message_simulator.py` - Message simulation for testing
- `template_variables.py` - Template variable management
- `pattern_learning.py` - Pattern recognition and learning
- `process_log_store.py` - Process logging system
- `whatsapp.py` - WhatsApp integration
- `ai_control_service.py` - AI control and management
- `user_update_service.py` - User update handling

#### Subdirectories
- `storage/` - Message storage
- `data_extraction/` - Data extraction utilities
  - `processor.py` - Main data processor
  - `rule_validator.py` - Rule validation system
  - `extractor.py` - Data extraction core
  - `processors/` - Data processors
  - `validators/` - Validation rules
  - `extractors/` - Data extractors
- `errors/` - Error handling
  - `data_extraction_errors.py` - Data extraction error definitions
  - `template_processing_errors.py` - Template processing errors
  - `stage_processing_errors.py` - Stage processing errors
- `models/` - Data models
  - `message_template_model.py` - Message template data model
  - `conversation_stage_model.py` - Conversation stage model
  - `business_entity_model.py` - Business entity model
- `stages/` - Processing stages
  - `stage_manager.py` - Stage management system
  - `state_manager.py` - State management
  - `transition_validator.py` - Stage transition validation
  - `handlers/` - Stage handlers
  - `models/` - Stage models
  - `manager/` - Stage management utilities
- `core/` - Core functionality
  - `errors.py` - Core error definitions
  - `context/` - Context management
  - `handler/` - Core handlers
  - `errors/` - Core error handling
- `services/` - Service layer
  - `template_service.py` - Template management service
  - `data_extraction_service.py` - Data extraction service
  - `stage_service.py` - Stage management service
  - `llm_service.py` - Language model service
  - `storage/` - Service storage
  - `monitoring/` - Service monitoring
  - `ai/` - AI services
- `templates/` - Message templates
  - `template_loader_service.py` - Template loading service
  - `validator.py` - Template validation
  - `renderer.py` - Template rendering
  - `variable_provider.py` - Variable management
  - `processors/` - Template processors
  - `variables/` - Template variables
  - `manager/` - Template management
- `variables/` - Variable management

### Update Services (`backend/update_services/`)
- `user_update_service.py` - User data update service
- `business_update_service.py` - Business data update service
- `base_update_service.py` - Base update service class

### Database Management (`backend/database/`)
- `__init__.py` - Package initialization
- `db.py` - Database operations
- `setup_database.py` - Database setup
- `db_config.py` - Database configuration
- `init_db.py` - Database initialization
- `__pycache__/` - Python cache

### Services (`backend/services/`)
- `conversation_summary_service.py` - Conversation summary service
- `ai/` - AI services
- `monitoring/` - Monitoring services
- `messaging/` - Messaging services

### Core (`backend/core/`)
- `__init__.py` - Package initialization
- `errors.py` - Core error definitions
- `__pycache__/` - Python cache

### Monitoring (`backend/monitoring/`)
- `enhanced_monitoring.py` - Enhanced monitoring system
- `populate_test_data.py` - Test data population
- `extraction_dashboard.py` - Data extraction dashboard
- `__pycache__/` - Python cache

### Routes (`backend/routes/`)
#### Core Routes
- `__init__.py` - Package initialization
- `auth_bp.py` - Authentication blueprint
- `health.py` - Health check routes
- `ping.py` - Ping endpoint
- `debug.py` - Debug routes

#### Business Management
- `business_management.py` - Business management routes
- `businesses.py` - Business operations
- `configuration.py` - Configuration routes
- `privacy.py` - Privacy settings

#### Message Handling
- `message_handling.py` - Message handling routes
- `messages.py` - Message operations
- `message_simulator.py` - Message simulation
- `conversation_management.py` - Conversation management
- `conversations.py` - Conversation operations
- `conversation_summary.py` - Conversation summaries

#### Template Management
- `template_management.py` - Template management routes
- `templates.py` - Template operations
- `template_test.py` - Template testing
- `template_variables.py` - Template variables

#### Stage Management
- `stage_management.py` - Stage management routes
- `stages.py` - Stage operations
- `transitions.py` - Stage transitions
- `routing.py` - Route management

#### User Management
- `user_management.py` - User management routes
- `users.py` - User operations
- `user_stats.py` - User statistics
- `agents.py` - Agent management

#### AI and Data
- `llm.py` - Language model routes
- `data_extraction.py` - Data extraction routes
- `monitoring_routes.py` - Monitoring endpoints
- `dashboard.py` - Dashboard routes

#### Testing and Utilities
- `tests.py` - Test routes
- `test_imports.py` - Import testing
- `check_routes.py` - Route checking
- `utils.py` - Route utilities
- `example_route.py` - Example routes
- `__pycache__/` - Python cache

### Schemas (`backend/schemas/`)
#### Core Schemas
- `configuration.json` - System configuration schema
- `message.json` - Message schema
- `business_create.json` - Business creation schema
- `business_event_property_schemas.json` - Business event properties

#### Business Schemas
- `businesses.json` - Business schema
- `owners.json` - Owner schema
- `products.json` - Product schema
- `orders.json` - Order schema
- `events.json` - Event schema

#### User and Agent Schemas
- `users.json` - User schema
- `agents.json` - Agent schema
- `conversations.json` - Conversation schema
- `messages.json` - Message schema

#### Template Schemas
- `templates.json` - Template schema
- `prompt_templates.json` - Prompt template schema
- `template_variables.json` - Template variables schema
- `template_variable_usage.json` - Variable usage schema

#### Processing Schemas
- `stages.json` - Stage schema
- `processing_stages.json` - Processing stage schema
- `pattern_data.json` - Pattern data schema
- `extraction_results.json` - Extraction results schema
- `extracted_data.json` - Extracted data schema

#### Monitoring Schemas
- `error_logs.json` - Error log schema
- `llm_calls.json` - LLM call schema

## Frontend Structure (`front-end/`)
### Core Files
- `package.json` - Node.js dependencies
- `package-lock.json` - Node.js dependency lock
- `jest.config.js` - Jest testing configuration
- `babel.config.js` - Babel configuration
- `.babelrc` - Babel runtime configuration
- `- Copy.env.txt` - Environment variables template
- `front end.zip` - Frontend archive

### Core Directories
- `src/` - Source code
- `public/` - Public assets
- `build/` - Production build
- `__mocks__/` - Test mocks
- `node_modules/` - Node.js dependencies

## Test Structure (`tests/`)
### Core Test Files
- `test_api_endpoints.py` - API endpoint tests
- `test_error_handling.py` - Error handling tests
- `test_template_system.py` - Template system tests
- `test_enhanced_extraction.py` - Data extraction tests

### Error Handling Tests
- `test_error_integration.py` - Error handling integration
- `test_error_decorators.py` - Error decorator tests
- `test_error_exceptions.py` - Custom exception tests
- `test_error_utils.py` - Error utility tests
- `test_error_middleware.py` - Error middleware tests
- `test_error_config.py` - Error configuration tests
- `test_error_handling_integration.py` - Error handling integration
- `test_error_response.py` - Error response format tests
- `test_error_logging.py` - Error logging tests
- `test_error_validation.py` - Error validation tests
- `test_error_recovery.py` - Error recovery tests
- `test_error_monitoring.py` - Error monitoring tests
- `test_error_tracking.py` - Error tracking tests

### Test Support
- `conftest.py` - Pytest configuration
- `setup_test_database.py` - Test database setup
- `test_factories.py` - Test data factories
- `factories.py` - Factory patterns
- `config/` - Test configuration
- `utils/` - Test utilities
- `migrations/` - Test migrations

### Test Utilities (`tests/utils/`)
- `seed_test_data.py` - Test data seeding
- `run_test_migrations.py` - Test database migrations

### Test Configuration (`tests/config/`)
- `test_db_config.py` - Test database configuration

## Planning Structure (`planning/`)
### Core Documentation
- `architecture.md` - System architecture
- `api_documentation.md` - API documentation
- `database_schema.md` - Database schema
- `template_system.md` - Template system
- `error_handling.md` - Error handling
- `authentication.md` - Authentication system

### Development & Testing
- `testing_strategy.md` - Testing approach
- `test_isolation.md` - Test isolation
- `test_data_seeding.md` - Test data management
- `implementation_guide.md` - Implementation details

### Deployment & Operations
- `deployment.md` - Deployment procedures
- `monitoring.md` - Monitoring setup
- `environment_variables.md` - Environment configuration

### Project Management
- `development_roadmap.md` - Project timeline
- `progress_plan.md` - Current progress
- `project_overview.md` - Project status
- `code_patterns.md` - Code patterns
- `troubleshooting.md` - Troubleshooting guide

### Additional Resources
- `message_handling_flow.md` - Message handling
- `stage_management.md` - Stage management
- `refactor_summary.md` - Refactoring details
- `frontend_guide.md` - Frontend documentation
- `file_structure.md` - Project file structure
- `README.md` - Project readme
- `to_saib.md` - SAIB documentation
- `core_logic.md` - Core logic documentation
- `ai_instructions.md` - AI instructions

## Documentation Structure (`docs/`)
### Migration Documentation
- `MIGRATION_GUIDE.md` - Database migration guide
- `DIRECTORY_STRUCTURE.md` - Project structure guide

### Template Documentation
- `template_testing.md` - Template testing guide
- `template_variables.md` - Template variables guide
- `template_variable_substitution.md` - Variable substitution guide

## Scripts Structure (`scripts/`)
### Documentation Scripts
- `update_docs.py` - Documentation update script
- `validate_docs.py` - Documentation validation
- `update_doc_content.py` - Content update script
- `fix_doc_structure.py` - Structure fix script
- `analyze_headings.py` - Heading analysis
- `enforce_heading_hierarchy.py` - Heading hierarchy enforcement
- `fix_complex_headings.py` - Complex heading fixes
- `fix_heading_levels.py` - Heading level fixes
- `fix_headings.py` - General heading fixes
- `update_dates.py` - Date update script
- `check_docs.py` - Documentation check script
- `requirements.txt` - Script dependencies

## Documentation Structure (`docs/`)
### Migration Documentation
- `MIGRATION_GUIDE.md` - Database migration guide
- `DIRECTORY_STRUCTURE.md` - Project structure guide

### Template Documentation
- `template_testing.md` - Template testing guide
- `template_variables.md` - Template variables guide
- `template_variable_substitution.md` - Variable substitution guide

Last Updated: 2025-05-12 