# Core Logic Explained

This document details some of the more complex or critical logic within the ICMP application.

## Three-Prompt System Implementation (`backend/routes/message_handling.py`)

The core message processing follows a three-prompt approach using OpenAI's API.

**Current Flow:**

1.  **Identify Stage and Templates:**
    *   The system retrieves the stage associated with the incoming message's `business_id`.
    *   From the stage, it extracts the template IDs (`stage_selection_template_id`, `data_extraction_template_id`, `response_generation_template_id`).
    *   These IDs reference templates in the `templates` table.
    *   **Note:** Templates are distinguished by their `template_type` field, with regular types (e.g., "stage_selection") used by stages and default types (e.g., "default_stage_selection") used as starting points.

2.  **Fetch Templates:**
    *   The system queries the `templates` table to retrieve the templates referenced by the stage.
    *   Each template contains a `content` field with placeholders (e.g., `{message}`, `{context}`) to be formatted.
    *   Templates may also define required variables and system prompts.

3.  **Fetch Context:**
    *   The system retrieves relevant conversation history from the `conversations` and `messages` tables.
    *   Context includes previous messages, stage information, and business context.

4.  **Stage Selection Prompt:**
    *   The `content` from the selection template is retrieved.
    *   Placeholders are formatted with the current user message and conversation context.
    *   The formatted prompt is sent to `openai_helper.call_openai`.
    *   The LLM response is processed to determine the next stage required.

5.  **Data Extraction Prompt:**
    *   The `content` from the extraction template is retrieved.
    *   Placeholders (e.g., `{message}`, `{context}`, `{stage}`) are formatted.
    *   The formatted prompt is sent to `openai_helper.call_openai`.
    *   The LLM response is processed to extract structured data (e.g., parse JSON, identify entities).

6.  **Response Generation Prompt:**
    *   The `content` from the generation template is retrieved.
    *   Placeholders (e.g., `{message}`, `{context}`, `{stage}`, `{extracted_data}`) are formatted.
    *   The formatted prompt is sent to `openai_helper.call_openai` to get the `final_response` for the user.

**Template Creation and Management:**

*   When creating a stage, empty templates are initially created or existing templates are referenced.
*   Templates with types like "default_stage_selection" serve as starting points that can be copied to create new templates.
*   The UI provides options to:
    *   Create new templates
    *   Apply default templates to existing templates
    *   Link templates to stages

**Key Assumptions/Implementation Notes:**

*   Relies on the `stages` table having the correct template ID columns.
*   Assumes `openai_helper.call_openai` takes a prompt string and returns the LLM's text response.
*   Templates in the `templates` table can be filtered by `template_type` to distinguish between regular and default templates.

## Authentication Decorators (`backend/auth.py`)

*   **`@require_api_key`:**
    *   Validates the global `ICMP_API_KEY` (from server config).
    *   Checks `Authorization: Bearer <key>` header first, then falls back to deprecated `icmpApiKey` cookie (fallback should likely be removed).
    *   Use Case: Protecting administrative endpoints (e.g., template management).
*   **`@require_business_api_key`:**
    *   Validates a business-specific API key.
    *   Extracts `business_id` from the route (`kwargs`) or request JSON/args.
    *   Extracts the `businessApiKey` value from the `businessApiKey` cookie first, then falls back to `Authorization: Bearer <businessApiKey>` header.
    *   Queries the `businesses` table to verify the extracted key matches the key stored for the extracted `business_id`.
    *   Use Case: Protecting endpoints related to specific business data (stages, messages, etc.).

## Stage Configuration (`backend/schemas/stages.json`, `backend/routes/stages.py`)

*   Stages are created via `POST /stages`.
*   The request body must conform to `backend/schemas/stages.json`.
*   This schema expects template ID references (`stage_selection_template_id`, etc.) that point to templates in the `templates` table.
*   The `create_stage` function in `routes/stages.py` creates the stage record with these template ID references.
*   Templates referenced by stages should have appropriate regular types (e.g., "stage_selection", "data_extraction", "response_generation").

## Template Management (`backend/schemas/templates.json`, `backend/routes/template_management.py`)

*   Templates are created and managed via endpoints defined in `routes/template_management.py`.
*   Templates can be of regular types (used directly by stages) or default types (used as starting points).
*   Default templates (with types like "default_stage_selection") serve as starter templates that can be copied to create new templates.
*   When creating or updating a stage, the associated templates can be either:
    *   Empty templates initially, with content added later
    *   Templates populated by copying content from default templates

## Related Documentation
- See [API Documentation](api_documentation.md) for endpoint details
- See [Database Schema](database_schema.md) for database structure
- See [Implementation Guide](implementation_guide.md) for system architecture
- See [Development Roadmap](development_roadmap.md) for project timeline

Last Updated: 2025-05-12
