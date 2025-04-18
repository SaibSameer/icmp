# API Specification

**Base URL:** `/` (relative to backend server, e.g., `http://localhost:5000`)

## Authentication

Two primary methods are used:

1.  **Master API Key (`ICMP_API_KEY`):**
    *   Required for administrative or server-to-server tasks.
    *   Passed via the `Authorization` header: `Authorization: Bearer <ICMP_API_KEY>`.
    *   Applies to routes decorated with `@require_api_key`.
2.  **Business API Key (`businessApiKey`):**
    *   Required for operations specific to a business.
    *   Passed automatically via the `businessApiKey` `HttpOnly` cookie after successful configuration via `/api/save-config`.
    *   Can potentially be passed via `Authorization: Bearer <businessApiKey>` for direct API access (needs confirmation based on `require_business_api_key` decorator logic).
    *   Applies to routes decorated with `@require_business_api_key`.

## Endpoints

*(Note: This is a preliminary list based on current files. Needs verification and expansion.)*

### Configuration & Health

*   **`GET /`**
    *   Description: Welcome message.
    *   Auth: None.
    *   Response (200 OK): `text/plain`
*   **`POST /api/save-config`**
    *   Description: Validates user, business, and business key; sets `businessApiKey` cookie.
    *   Auth: None (entry point for setting cookie).
    *   Request Body: `application/json` (Schema: See notes below)
        ```json
        {
          "userId": "uuid",
          "businessId": "uuid",
          "businessApiKey": "string"
        }
        ```
    *   Response (200 OK): `application/json`
        ```json
        {"success": true}
        ```
    *   Response (400 Bad Request): `{"success": false, "error": "Missing parameters | Invalid parameter types"}`
    *   Response (401 Unauthorized): `{"success": false, "error": "Invalid credentials: ..."}`
*   **`POST /validate_config`**
    *   Description: Validates a full set of config details including the master key. (Purpose/necessity might need review after refactor).
    *   Auth: `@require_api_key` (Master Key via Bearer).
    *   Request Body: `application/json`
        ```json
        {
          "userId": "uuid",
          "businessId": "uuid",
          "apiKey": "string", // Master ICMP_API_KEY
          "businessApiKey": "string"
        }
        ```
    *   Response (200 OK): `{"isValid": true}`
    *   Response (400/401/500): See `app.py` for details.
*   **`GET /health`**
    *   Description: Health check endpoint.
    *   Auth: None.
    *   Response (200 OK): `{"status": "ok"}`
*   **`GET /ping`**
    *   Description: Simple ping endpoint.
    *   Auth: None.
    *   Response (200 OK): `{"message": "pong"}`

### Business Management

*   **`POST /businesses`**
    *   Description: Creates a new business.
    *   Auth: `@require_api_key` (Master Key via Bearer).
    *   Request Body: `application/json` (Schema: `backend/schemas/business_create.json` - Needs update? Compare with `businesses.py` route schema)
    *   Response (201 Created): `{"message": "Business created", "business_id": "uuid", "api_key": "string"}`
    *   Response (400/500): Error details.
*   **`GET /businesses/{business_id}`**
    *   Description: Retrieves details for a specific business.
    *   Auth: `@require_business_api_key` (Business Key via Cookie/Bearer).
    *   Path Params: `business_id` (UUID).
    *   Response (200 OK): `application/json` (Business details)
    *   Response (400/401/404/500): Error details.

### Stage Management

*   **`POST /stages`**
    *   Description: Creates a new stage for a business, including template configurations.
    *   Auth: `@require_business_api_key` (Business Key via Cookie/Bearer).
    *   Request Body: `application/json` (Schema: `backend/schemas/stages.json` - Updated).
    *   Response (201 Created): `{"stage_id": "uuid"}`
    *   Response (400/401/500): Error details.
*   **`GET /stages`** (Example - Needs Implementation)
    *   Description: Retrieves stages, likely filtered by `business_id`.
    *   Auth: `@require_business_api_key`.
    *   Query Params: `?business_id=uuid`.
    *   Response (200 OK): Array of stage objects.

### Default Template Management

*   **`POST /templates`** (or `/defaultTemplates` - Check `template_management.py`)
    *   Description: Creates a global default template.
    *   Auth: `@require_api_key` (Master Key via Bearer).
    *   Request Body: `application/json` (Schema defined inline in `template_management.py`).
    *   Response (201 Created): `{"template_id": "uuid"}`
    *   Response (400/500): Error details.
*   **`GET /templates`** (or `/defaultTemplates`)
    *   Description: Retrieves all global default templates.
    *   Auth: `@require_api_key` (Master Key via Bearer).
    *   Response (200 OK): Array of template objects.

### Message Handling

*   **`POST /message`**
    *   Description: Handles an incoming user message for a business.
    *   Auth: `@require_business_api_key` (Business Key via Cookie/Bearer).
    *   Request Body: `application/json` (Schema: `backend/schemas/message.json`).
    *   Response (200 OK): `{"response": "AI generated response", "conversation_id": "uuid"}`
    *   Response (400/401/404/500): Error details.

### Conversation Management

*   **`GET /conversations/{user_id}`**
    *   Description: Retrieves conversations for a specific user.
    *   Auth: `@require_business_api_key` (Business Key via Cookie/Bearer). **Note:** Additional authorization needed to link user_id to the authenticated business.
    *   Path Params: `user_id` (UUID).
    *   Response (200 OK): Array of conversation objects.
    *   Response (400/401/403/500): Error details.

### User Management

*   **`POST /users`**
    *   Description: Creates a new user.
    *   Auth: `@require_api_key` (Master Key via Bearer) - Verify this intended auth level.
    *   Request Body: `application/json` (Schema: `backend/schemas/users.json`).
    *   Response (201 Created): `{"user_id": "uuid"}`
    *   Response (400/500): Error details.
*   **`GET /users`**
    *   Description: Retrieves all users.
    *   Auth: `@require_api_key` (Master Key via Bearer).
    *   Response (200 OK): Array of user objects.
    *   Response (500): Error details.

*(Add other endpoints as needed)* 