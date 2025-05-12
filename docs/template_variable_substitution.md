# Template Variable Substitution Documentation

## Overview
The template variable substitution system allows for dynamic content generation by replacing variables in templates with actual values. This system supports both frontend and backend implementations, providing a consistent way to handle dynamic content across the application.

## Variable Syntax
The system supports two types of variable syntax:
- Single braces: `{variable_name}`
- Double braces: `{{variable_name}}`

**Note:** While both formats are supported, it is recommended to use double braces `{{variable_name}}` for consistency and clarity.

## Usage Examples

### Basic Variable Substitution
```html
<!-- Template -->
Hello {{user_name}}! Welcome to {{platform_name}}.

<!-- Context -->
{
    "user_name": "John",
    "platform_name": "Our Platform"
}

<!-- Result -->
Hello John! Welcome to Our Platform.
```

### System Prompt Variables
```html
<!-- Template with System Prompt -->
{
    "content": "Hello {{user_name}}!",
    "system_prompt": "You are speaking with {{user_name}} on {{platform_name}}."
}

<!-- Result -->
{
    "content": "Hello John!",
    "system_prompt": "You are speaking with John on Our Platform."
}
```

## Implementation Details

### Frontend Implementation
The frontend implementation is available in `variable_test.html` and provides:
- Variable testing interface
- Real-time substitution preview
- Variable validation
- Error handling

### Backend Implementation
The backend implementation in `template_service.py` provides:
- Template processing
- Variable extraction
- Context application
- Error handling

## Best Practices

1. **Variable Naming**
   - Use descriptive names
   - Use snake_case format
   - Avoid special characters
   - Example: `{{user_first_name}}`, `{{last_message_content}}`

2. **Error Handling**
   - Always provide default values
   - Handle missing variables gracefully
   - Log substitution errors

3. **Security**
   - Sanitize variable values
   - Validate variable names
   - Prevent XSS attacks

4. **Performance**
   - Cache frequently used templates
   - Minimize nested variables
   - Use efficient substitution methods

## Common Issues and Solutions

1. **Missing Variables**
   - Problem: Variable not found in context
   - Solution: System will use `[Missing: variable_name]` as fallback

2. **Invalid Syntax**
   - Problem: Malformed variable syntax
   - Solution: Use proper brace format and validate before substitution

3. **Performance Issues**
   - Problem: Slow substitution with many variables
   - Solution: Cache templates and optimize variable extraction

## API Reference

### Frontend API
```javascript
// Test variable substitution
function testSubstitution(template, variables) {
    // Returns substituted content
}

// Extract variables from template
function extractVariables(template) {
    // Returns array of variable names
}
```

### Backend API
```python
# Apply template with context
def apply_template(template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply template with variable substitution.
    
    Args:
        template: Template object with content and metadata
        context: Context dictionary with variable values
        
    Returns:
        Dictionary with processed template content and system prompt
    """
```

## Migration Guide

### From Single to Double Braces
1. Identify templates using single braces
2. Update to double brace syntax
3. Test substitution
4. Update documentation

### Adding New Variables
1. Define variable name and format
2. Add to template
3. Provide context value
4. Test substitution

## Testing

### Manual Testing
1. Use the variable testing tool
2. Verify substitution results
3. Check error handling
4. Validate security measures

### Automated Testing
1. Unit tests for substitution
2. Integration tests for templates
3. Performance benchmarks
4. Security tests

## Support and Maintenance

### Troubleshooting
- Check variable names
- Verify context values
- Review error logs
- Test in isolation

### Updates and Changes
- Document all changes
- Maintain backward compatibility
- Update test cases
- Review security measures

## Contributing
1. Follow coding standards
2. Add test cases
3. Update documentation
4. Review security implications

## Version History
- v1.0.0: Initial implementation
- v1.1.0: Added double brace support
- v1.2.0: Enhanced security features
- v1.3.0: Performance optimizations

## Contact
For questions or issues, please contact the development team or create an issue in the repository. 