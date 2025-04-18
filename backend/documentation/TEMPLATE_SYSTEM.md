# Template System

## Overview

The template system is a core component of the ICMP Events API, responsible for managing and applying templates used in various stages of message processing. Templates contain text with variable placeholders that are substituted at runtime with context-specific values.

## Database Schema

### Templates Table

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

Key fields:
- `template_id`: Unique identifier for the template
- `business_id`: References the business that owns this template
- `template_name`: Human-readable name for the template
- `template_type`: Categorizes templates (e.g., stage_selection, data_extraction, response_generation)
- `content`: The main template text with variable placeholders
- `system_prompt`: Optional system prompt for LLM context setting

### Legacy Schema Migration

Previously, templates were stored in the `prompt_templates` table:

```sql
CREATE TABLE prompt_templates (
    template_id CHARACTER VARYING(255) PRIMARY KEY NOT NULL,
    template_text TEXT NOT NULL,
    description TEXT,
    variables TEXT[] NOT NULL DEFAULT '{}',
    template_name CHARACTER VARYING(255),
    template_type CHARACTER VARYING(50) DEFAULT 'stage_selection'
);
```

We've migrated all functionality to use the `templates` table. A migration script is available at `backend/migrations/01_cleanup_template_tables.sql` to ensure all data is properly migrated and the redundant table can be safely removed.

## Template Types

The system supports several template types:

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

## Template Variables

Templates support variable substitution using both `{variable_name}` and `{{variable_name}}` syntax. Variables are automatically extracted from template content and can be populated at runtime with values from:

- User information
- Conversation context
- Business data
- Stage-specific data

Example template with variables:
```
Hello {{user_name}}, welcome to {{business_name}}! 
Your last 10 messages: {{last_10_messages}}
```

### Variable Providers

The system uses a modular variable provider system located in `backend/message_processing/variables/`. Each variable has its own dedicated provider file:

1. User Variables:
   - `user_name.py`: Provides the user's full name
   - `user_message.py`: Provides the current message content

2. Business Variables:
   - `business_name.py`: Provides the business name

3. Conversation Variables:
   - `last_10_messages.py`: Provides the last 10 messages in the conversation
   - `conversation_history.py`: Provides the full conversation history
   - `N.py`: Provides the message count

4. Stage Variables:
   - `available_stages.py`: Provides detailed stage information
   - `stage_list.py`: Provides a list of stage names

5. Utility Variables:
   - `current_time.py`: Provides the current time
   - `current_date.py`: Provides the current date

### Adding New Variables

To add a new variable:

1. Create a new file in `backend/message_processing/variables/`
2. Define a provider function using the `@TemplateVariableProvider.register_provider` decorator
3. Add the import to `backend/message_processing/variables/__init__.py`

Example variable provider:
```python
@TemplateVariableProvider.register_provider('my_variable')
def provide_my_variable(conn, **kwargs) -> str:
    return "my value"
```

## Backend Implementation

### Template Service

The `TemplateService` class in `backend/message_processing/template_service.py` provides core functionality:

- `get_template()`: Retrieves a template by ID from the database
- `apply_template()`: Performs variable substitution on a template
- `build_context()`: Constructs a context object for variable substitution

### API Endpoints

Template-related API endpoints are defined in:

1. `backend/routes/templates.py`: Core CRUD operations
   - GET `/templates`: List all templates
   - POST `/templates`: Create a new template
   - GET `/templates/{template_id}`: Get a specific template
   - PUT `/templates/{template_id}`: Update a template
   - DELETE `/templates/{template_id}`: Delete a template

2. `backend/routes/template_management.py`: Additional management endpoints
   - GET `/templates/default-templates`: List default templates
   - GET `/templates/by-type/{template_type}`: List templates by type
   - GET `/templates/by-business/{business_id}`: List templates by business

## Frontend Components

The frontend provides UI components for template management:

1. `TemplateManagement.js`: Main component for listing and managing templates
2. `TemplateEditor.js`: Component for creating and editing templates
3. `TemplateSection.js`: Component for creating templates within another view

These components allow users to:
- Create, edit, and delete templates
- Preview templates with sample data
- Organize templates by type and business
- Extract and manage variables

## Integration with Stages

Templates are integrated with the stage system:

1. Each stage references three template types:
   - `stage_selection_template_id`: Determines if the stage should handle a message
   - `data_extraction_template_id`: Extracts data from the message
   - `response_generation_template_id`: Generates a response

2. The stage processing flow:
   - Evaluate stage selection templates to choose a stage
   - Use the selected stage's data extraction template
   - Generate a response using the response generation template

## Best Practices

When working with templates:

1. **Variable Naming**:
   - Use descriptive names for variables
   - Follow dot notation for nested properties (e.g., `user.first_name`)
   
2. **Template Organization**:
   - Organize templates by logical function
   - Use consistent naming conventions
   - Include descriptive template names

3. **Error Handling**:
   - Include fallback text for missing variables
   - Design templates to gracefully handle missing context

4. **Testing**:
   - Preview templates before deployment
   - Test with a variety of input data

## Troubleshooting

Common issues and solutions:

1. **Missing Variables**: If variables aren't being substituted, check:
   - Variable names match in template and context
   - Context is being properly built
   - Variable syntax uses correct braces `{like_this}`

2. **Template Selection Issues**: If wrong templates are being used:
   - Verify template type is correct
   - Check stage template IDs
   - Examine stage selection logic

3. **Performance Concerns**: For template performance issues:
   - Keep templates reasonably sized
   - Limit the number of variables
   - Consider caching frequently used templates 