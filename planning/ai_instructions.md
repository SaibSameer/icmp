# AI Assistant Instructions

## Project Context
This is a messaging integration backend service that handles WhatsApp and Facebook Messenger communications, with AI-powered conversation management. The project is currently undergoing reorganization and improvement.

## Key Principles
1. **Code Organization**
   - Follow the established directory structure
   - Keep related functionality together
   - Maintain clear separation of concerns
   - Use consistent naming conventions

2. **Error Handling**
   - Always implement proper error handling
   - Log errors with sufficient context
   - Provide meaningful error messages
   - Include error recovery mechanisms

3. **Documentation**
   - Document all new code
   - Update existing documentation
   - Include examples where helpful
   - Keep documentation in sync with code

4. **Testing**
   - Write tests for new functionality
   - Maintain test coverage
   - Include edge cases
   - Document test scenarios

## Working with the Codebase

### Directory Structure
```
backend/
├── ai/                 # AI-related functionality
├── database/          # Database operations and models
├── message_processing/ # Message handling and routing
├── template_management/ # Template system
└── utils/             # Utility functions
```

### Key Files
1. **Configuration**
   - `backend/config.py` - Main configuration
   - `backend/database/db_config.py` - Database configuration
   - `.env` - Environment variables

2. **Core Components**
   - `backend/app.py` - Main application
   - `backend/database/db.py` - Database operations
   - `backend/message_processing/messenger.py` - Messenger integration
   - `backend/message_processing/whatsapp.py` - WhatsApp integration
   - `backend/ai/openai_helper.py` - AI integration

### Common Tasks

1. **Adding New Features**
   - Create appropriate directory if needed
   - Follow existing patterns
   - Update documentation
   - Add tests
   - Update import statements

2. **Modifying Existing Code**
   - Review related files
   - Check dependencies
   - Update tests
   - Update documentation
   - Verify functionality

3. **Fixing Bugs**
   - Reproduce the issue
   - Identify root cause
   - Implement fix
   - Add test case
   - Update documentation

4. **Code Review**
   - Check code style
   - Verify error handling
   - Review documentation
   - Check test coverage
   - Validate functionality

## Best Practices

1. **Code Style**
   - Follow PEP 8
   - Use meaningful names
   - Keep functions focused
   - Add type hints
   - Include docstrings

2. **Error Handling**
   - Use specific exceptions
   - Include error context
   - Implement retry logic
   - Log errors properly
   - Handle edge cases

3. **Testing**
   - Write unit tests
   - Include integration tests
   - Test edge cases
   - Mock external services
   - Verify error handling

4. **Documentation**
   - Keep it up to date
   - Include examples
   - Document assumptions
   - Explain complex logic
   - Note limitations

## Common Patterns

1. **Database Operations**
   ```python
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

2. **Error Handling**
   ```python
   try:
       # Operation
   except SpecificError as e:
       logger.error(f"Error occurred: {str(e)}", exc_info=True)
       raise CustomError("User-friendly message") from e
   ```

3. **API Responses**
   ```python
   return jsonify({
       "status": "success",
       "data": result,
       "message": "Operation completed"
    }), 200
   ```

## Important Considerations

1. **Security**
   - Validate all inputs
   - Sanitize outputs
   - Use secure defaults
   - Follow security best practices
   - Handle sensitive data properly

2. **Performance**
   - Optimize database queries
   - Use connection pooling
   - Implement caching
   - Monitor resource usage
   - Handle timeouts

3. **Maintainability**
   - Keep code DRY
   - Use clear abstractions
   - Document decisions
   - Follow patterns
   - Write clean code

4. **Reliability**
   - Handle edge cases
   - Implement retries
   - Add monitoring
   - Log important events
   - Validate assumptions

## Getting Help
- Check the planning directory for project documentation
- Review the architecture.md for system design
- Consult the development_roadmap.md for current status
- Look at the codebase_analysis directory for detailed analysis
- Check the cleanup_plans directory for ongoing improvements

Last Updated: 2025-05-12
