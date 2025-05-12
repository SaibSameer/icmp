# Template System Documentation

## Overview
The template system is a core component of the ICMP Events API, responsible for managing and applying templates used in various stages of message processing. Templates contain text with variable placeholders that are substituted at runtime with context-specific values.

## Implementation Details

### Database Schema
The system uses the `templates` table with the following structure:
```sql
CREATE TABLE templates (
    template_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id),
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    system_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Template Types
1. **Stage Selection Templates** (`stage_selection`)
   - Used to determine which stage should handle a user's message
   - Example: Analyzing user intent to route to appropriate stages

2. **Data Extraction Templates** (`data_extraction`)
   - Used to extract structured data from user messages
   - Example: Extracting order numbers, names, or other entities

3. **Response Generation Templates** (`response_generation`)
   - Used to generate AI responses based on extracted data and context
   - Example: Creating personalized replies incorporating user information

4. **Default Templates**
   - Prefixed versions of the above (e.g., `default_stage_selection`)
   - Used as fallbacks when business-specific templates aren't available

### Variable System
Templates support variable substitution using both `{variable_name}` and `{{variable_name}}` syntax. Variables are automatically extracted from template content and can be populated at runtime with values from:
- User information
- Conversation context
- Business data
- Stage-specific data

#### Variable Providers
The system uses a modular variable provider system located in `backend/message_processing/variables/`:

1. Core Variable Provider:
   - `TemplateVariableProvider` class in `backend/message_processing/template_variables.py`
   - Supports variable registration with metadata (description, auth requirements, validation rules)
   - Handles variable extraction, validation, and value generation
   - Provides caching and performance optimization

2. User Variables:
   - `user_name.py`: Provides the user's full name
   - `user_message.py`: Provides the current message content
   - `user_preferences.py`: Provides user-specific preferences

3. Business Variables:
   - `business_name.py`: Provides the business name
   - `business_info.py`: Provides detailed business information
   - `business_settings.py`: Provides business-specific settings

4. Conversation Variables:
   - `last_10_messages.py`: Provides the last 10 messages
   - `conversation_history.py`: Provides full conversation history
   - `ai_conversation_history.py`: Provides AI-enhanced conversation history
   - `conversation_context.py`: Provides current conversation context

5. Stage Variables:
   - `available_stages.py`: Provides detailed stage information
   - `agent_stages.py`: Provides stages associated with specific agents
   - `stage_context.py`: Provides current stage context

6. Utility Variables:
   - `current_time.py`: Provides the current time
   - `current_date.py`: Provides the current date
   - `environment.py`: Provides environment-specific values

### Implementation Components

#### Template Manager
The `TemplateManager` class in `backend/template_management/template_manager.py` provides core functionality:
- `render(template_id, context)`: Renders a template with variable substitution
- `get_template(template_id)`: Retrieves template details by ID
- `validate_template(template_id)`: Validates template syntax and variables
- `cache_template(template_id)`: Caches template for improved performance

#### Template Renderer
The `TemplateRenderer` class in `backend/message_processing/templates/renderer.py` handles:
- Text template rendering with variable substitution
- Context application
- Error handling
- Performance optimization through caching

#### Redis Integration
The template system uses Redis for:
1. Template caching
2. Variable value caching
3. Context storage
4. Performance optimization

Example Redis usage:
```python
# Cache template
redis_manager.set_state(f"template:{template_id}", template_data)

# Cache variable values
redis_manager.set_state(f"var:{variable_name}", variable_value)

# Get cached template
template_data = redis_manager.get_state(f"template:{template_id}")
```

#### API Endpoints
Template-related endpoints are defined in:
1. `backend/routes/templates.py`: Core CRUD operations
2. `backend/routes/template_management.py`: Additional management endpoints
3. `backend/routes/template_variables.py`: Variable management endpoints

#### Frontend Components
The frontend provides UI components for template management:
1. `TemplateManagement.js`: Main component for listing and managing templates
2. `TemplateEditor.js`: Component for creating and editing templates
3. `TemplateSection.js`: Component for creating templates within another view
4. `VariableManager.js`: Component for managing template variables

## Integration with Stages
Templates are integrated with the stage system:
1. Each stage references three template types:
   - `stage_selection_template_id`
   - `data_extraction_template_id`
   - `response_generation_template_id`

2. The stage processing flow:
   - Evaluate stage selection templates
   - Use data extraction template
   - Generate response using response generation template
   - Cache results in Redis for performance

## Best Practices
1. **Variable Naming**:
   - Use descriptive names
   - Follow snake_case format
   - Avoid special characters
   - Example: `{{user_first_name}}`, `{{last_message_content}}`

2. **Template Organization**:
   - Organize by logical function
   - Use consistent naming conventions
   - Include descriptive names
   - Cache frequently used templates

3. **Error Handling**:
   - Include fallback text
   - Design for graceful failure
   - Log template rendering errors
   - Implement retry mechanisms

4. **Testing**:
   - Preview before deployment
   - Test with various inputs
   - Validate variable substitution
   - Test caching behavior

5. **Performance**:
   - Cache templates and variables
   - Use Redis for state management
   - Implement lazy loading
   - Monitor cache hit rates

## Troubleshooting
Common issues and solutions:
1. **Missing Variables**:
   - Check variable names
   - Verify context building
   - Confirm syntax
   - Check Redis cache

2. **Template Selection**:
   - Verify template type
   - Check stage template IDs
   - Review selection logic
   - Validate cache state

3. **Performance**:
   - Keep templates concise
   - Limit variables
   - Use Redis caching
   - Monitor cache usage

4. **Redis Issues**:
   - Check Redis connection
   - Verify cache keys
   - Monitor memory usage
   - Implement fallback mechanisms

## Related Documentation
- See `planning/api_documentation.md` for API endpoints
- See `planning/database_schema.md` for database structure
- See `planning/code_patterns.md` for implementation patterns
- See `planning/testing_strategy.md` for testing guidelines

Last Updated: 2025-05-12
