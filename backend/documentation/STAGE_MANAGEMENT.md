# Stage Management System

## Overview

The Stage Management System is a core component of the ICMP platform that allows businesses to define, configure, and manage conversation stages. Each stage represents a specific point in a conversation flow and contains configuration for how the system should handle messages at that point.

## Components

### Stage View

The stage view component (`StageView.jsx`) provides a read-only view of stage details, including:

1. **Basic Information**
   - Stage Name
   - Description
   - Type (e.g., conversation, response, form)
   - Stage ID
   - Business ID
   - Agent ID (if applicable)

2. **Template Configuration**
   - Stage Selection Template
     - Template ID
     - Template Name
   - Data Extraction Template
     - Template ID
     - Template Name
   - Response Generation Template
     - Template ID
     - Template Name

3. **Creation Information**
   - Creation Date/Time

### Stage Editor

The stage editor component allows users to create and modify stages. It includes:

1. **Basic Information Form**
   - Name input
   - Description input
   - Type selection
   - Agent assignment (optional)

2. **Template Configuration**
   - Template selection for each type:
     - Stage Selection
     - Data Extraction
     - Response Generation
   - Template preview
   - Template configuration options

## Database Schema

The stages table schema (from `stages` table in PostgreSQL):

```sql
CREATE TABLE stages (
    stage_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    agent_id UUID,  -- Optional link to a specific agent
    stage_name TEXT NOT NULL,
    stage_description TEXT NOT NULL,
    stage_type TEXT NOT NULL,  -- e.g., 'conversation', 'response', 'form'
    stage_selection_template_id UUID NOT NULL REFERENCES templates(template_id),
    data_extraction_template_id UUID NOT NULL REFERENCES templates(template_id),
    response_generation_template_id UUID NOT NULL REFERENCES templates(template_id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## API Endpoints

### GET /stages

Lists all stages for a business.

**Query Parameters:**
- `business_id` (required): UUID of the business
- `agent_id` (optional): UUID of an agent to filter stages

**Response:**
```json
[
    {
        "stage_id": "uuid",
        "stage_name": "string",
        "stage_description": "string",
        "stage_type": "string",
        "business_id": "uuid",
        "agent_id": "uuid",
        "stage_selection_template_id": "uuid",
        "data_extraction_template_id": "uuid",
        "response_generation_template_id": "uuid",
        "created_at": "timestamp"
    }
]
```

### GET /stages/{stage_id}

Retrieves details for a specific stage.

**Query Parameters:**
- `business_id` (required): UUID of the business

**Response:**
```json
{
    "stage_id": "uuid",
    "stage_name": "string",
    "stage_description": "string",
    "stage_type": "string",
    "business_id": "uuid",
    "agent_id": "uuid",
    "stage_selection_template_id": "uuid",
    "data_extraction_template_id": "uuid",
    "response_generation_template_id": "uuid",
    "created_at": "timestamp",
    "stage_selection_config": {
        "template_id": "uuid",
        "template_name": "string",
        "content": "string",
        "system_prompt": "string",
        "variables": []
    },
    "data_extraction_config": {
        "template_id": "uuid",
        "template_name": "string",
        "content": "string",
        "system_prompt": "string",
        "variables": []
    },
    "response_generation_config": {
        "template_id": "uuid",
        "template_name": "string",
        "content": "string",
        "system_prompt": "string",
        "variables": []
    }
}
```

### POST /stages

Creates a new stage.

**Request Body:**
```json
{
    "business_id": "uuid",
    "stage_name": "string",
    "stage_description": "string",
    "stage_type": "string",
    "agent_id": "uuid",  // optional
    "stage_selection_template_id": "uuid",
    "data_extraction_template_id": "uuid",
    "response_generation_template_id": "uuid"
}
```

### PUT /stages/{stage_id}

Updates an existing stage.

**Request Body:**
```json
{
    "business_id": "uuid",
    "stage_name": "string",
    "stage_description": "string",
    "stage_type": "string",
    "agent_id": "uuid",  // optional
    "stage_selection_template_id": "uuid",
    "data_extraction_template_id": "uuid",
    "response_generation_template_id": "uuid"
}
```

## Frontend Routes

- `/stages` - Stage list/management view
- `/stages/:stageId` - Stage detail view
- `/stage-editor/:stageId` - Stage editor view
- `/stage-editor/new` - New stage creation view

## Usage Examples

### Viewing a Stage

1. Navigate to the stage list at `/stages`
2. Click on a stage to view its details
3. The stage view will show:
   - Basic information about the stage
   - Template configurations
   - Creation timestamp

### Editing a Stage

1. View a stage's details
2. Click the "Edit Stage" button
3. Modify the stage's information in the editor
4. Save changes

### Creating a New Stage

1. Navigate to the stage list
2. Click "Create Stage"
3. Fill in the required information:
   - Stage name and description
   - Stage type
   - Template selections
4. Save the new stage

## Error Handling

The stage management system includes error handling for:
- Invalid stage IDs
- Missing or invalid business IDs
- Template configuration errors
- Database connection issues
- Authentication/authorization failures

## Security Considerations

1. **Authentication**
   - All stage endpoints require a valid business API key
   - API key is passed via secure HttpOnly cookie

2. **Authorization**
   - Stages can only be accessed by their owning business
   - Business ID validation on all requests

3. **Data Validation**
   - Input validation on all stage fields
   - Template ID validation against prompt_templates table
   - Business ID validation against businesses table 