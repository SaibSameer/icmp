# Stage Management System

## Overview
The Stage Management System is a core component of the ICMP platform that allows businesses to define, configure, and manage conversation stages. Each stage represents a specific point in a conversation flow and contains configuration for how the system should handle messages at that point.

## Implementation Details

### Database Schema
The stages table schema:
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

### Redis Integration
The stage management system uses Redis for:
1. **Stage State Management**
   - Current stage tracking
   - Stage transition history
   - Stage-specific data caching

2. **Performance Optimization**
   - Stage configuration caching
   - Template caching
   - State persistence

3. **Implementation**
```python
class StageService:
    def __init__(self, db_pool, redis_manager):
        self.db_pool = db_pool
        self.redis_manager = redis_manager

    def get_current_stage(self, conversation_id):
        """Get current stage from Redis."""
        return self.redis_manager.get_state(f"stage:{conversation_id}")

    def set_current_stage(self, conversation_id, stage_id):
        """Set current stage in Redis."""
        self.redis_manager.set_state(f"stage:{conversation_id}", stage_id)

    def clear_stage_state(self, conversation_id):
        """Clear stage state from Redis."""
        self.redis_manager.delete_state(f"stage:{conversation_id}")
```

### Frontend Components

#### Stage View
The stage view component (`StageView.jsx`) provides:
1. **Basic Information**
   - Stage Name
   - Description
   - Type
   - Stage ID
   - Business ID
   - Agent ID

2. **Template Configuration**
   - Stage Selection Template
   - Data Extraction Template
   - Response Generation Template

3. **Creation Information**
   - Creation Date/Time

4. **Stage State**
   - Current stage status
   - Stage transition history
   - Stage-specific data

#### Stage Editor
The stage editor component includes:
1. **Basic Information Form**
   - Name input
   - Description input
   - Type selection
   - Agent assignment

2. **Template Configuration**
   - Template selection for each type
   - Template preview
   - Configuration options

3. **State Management**
   - Stage state configuration
   - Transition rules
   - Data persistence settings

### API Endpoints

#### GET /stages
Lists all stages for a business.

**Query Parameters:**
- `business_id` (required): UUID of the business
- `agent_id` (optional): UUID of an agent to filter stages

#### GET /stages/{stage_id}
Retrieves details for a specific stage.

**Query Parameters:**
- `business_id` (required): UUID of the business

#### POST /stages
Creates a new stage.

#### PUT /stages/{stage_id}
Updates an existing stage.

#### GET /stages/{stage_id}/state
Retrieves the current state of a stage.

#### PUT /stages/{stage_id}/state
Updates the state of a stage.

### Frontend Routes
- `/stages` - Stage list/management view
- `/stages/:stageId` - Stage detail view
- `/stage-editor/:stageId` - Stage editor view
- `/stage-editor/new` - New stage creation view
- `/stages/:stageId/state` - Stage state management view

## Usage Examples

### Viewing a Stage
1. Navigate to `/stages`
2. Click on a stage to view details
3. View basic information and template configurations
4. Check current stage state and history

### Editing a Stage
1. View stage details
2. Click "Edit Stage"
3. Modify information
4. Configure state management
5. Save changes

### Creating a New Stage
1. Navigate to stage list
2. Click "Create Stage"
3. Fill in required information
4. Configure state management
5. Save new stage

### Managing Stage State
1. View stage details
2. Navigate to state management
3. View current state
4. Update state if needed
5. Monitor state transitions

## Error Handling
The system handles:
- Invalid stage IDs
- Missing business IDs
- Template configuration errors
- Database connection issues
- Authentication failures
- Redis connection issues
- State management errors

## Security
1. **Authentication**
   - Valid business API key required
   - Secure HttpOnly cookie

2. **Authorization**
   - Business-specific access
   - Business ID validation

3. **Data Validation**
   - Input validation
   - Template ID validation
   - Business ID validation
   - State validation

4. **Redis Security**
   - Secure Redis connection
   - Data encryption
   - Access control
   - State isolation

## Performance Optimization
1. **Caching Strategy**
   - Stage configuration caching
   - Template caching
   - State caching
   - Transition history caching

2. **State Management**
   - Efficient state updates
   - State persistence
   - State recovery
   - State cleanup

## Related Documentation
- See `planning/template_system.md` for template details
- See `planning/api_documentation.md` for API endpoints
- See `planning/database_schema.md` for database structure
- See `planning/code_patterns.md` for implementation patterns
- See `planning/testing_strategy.md` for testing guidelines

Last Updated: 2025-05-12
