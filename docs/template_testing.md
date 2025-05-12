# Template Testing Documentation

This document describes how to test templates in the React frontend.

## Template Test Page

The Template Test Page (`TemplateTestPage.jsx`) provides a dedicated interface for testing templates.

### Features
- Select a template from a dropdown list
- View template content and system prompt
- Test template with custom context
- View test results in real-time

### Usage
1. Navigate to the Template Test Page
2. Select a template from the dropdown
3. (Optional) Enter custom context in JSON format
4. Click "Test" to run the template test
5. View the results in the test result section

### Context Override
You can provide custom context in JSON format to override default variables:
```json
{
  "user_name": "Custom User",
  "business_name": "Custom Business",
  "current_time": "12:00:00"
}
```

## Template Edit Testing

The Template Edit interface (`TemplateEdit.jsx`) includes built-in testing functionality.

### Features
- Test templates while editing
- View test results in the same interface
- Test with specific user ID

### Usage
1. Open a template for editing
2. Enter a Test User ID
3. Click "Test" to run the template test
4. View the results below the test button

## API Integration

The template testing functionality uses the following API endpoint:

```javascript
POST /api/template-test
{
    "business_id": "uuid",
    "agent_id": "uuid (optional)",
    "template_content": {
        "template_name": "string",
        "content": "string",
        "system_prompt": "string",
        "template_type": "string"
    },
    "test_mode": true
}
```

### Response Format
```javascript
{
    "content": "string", // Processed template content
    "results": "string", // Alternative result format
    "error": "string"    // Error message if test fails
}
```

## Available Variables

When testing templates, you can use any of the template variables documented in `template_variables.md`. The test interface will automatically substitute these variables with their actual values.

### Common Test Scenarios

1. Testing with default variables:
   - Use the basic test interface without context override
   - System will use actual business and user data

2. Testing with custom context:
   - Use the context override field
   - Provide custom values for specific variables
   - Useful for testing edge cases

3. Testing with specific user:
   - Use the Test User ID field
   - Test how the template behaves with different users

## Error Handling

The test interface handles various error cases:
- Invalid template content
- Missing required variables
- Invalid context override JSON
- API errors
- Network issues

Error messages are displayed in the interface to help diagnose issues.

## Best Practices

1. Always test templates with realistic data
2. Test edge cases using context override
3. Verify variable substitution
4. Check system prompt integration
5. Test with different user contexts
6. Validate error handling 