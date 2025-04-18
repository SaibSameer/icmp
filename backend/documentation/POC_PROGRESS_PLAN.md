# ICMP POC - Recommended Progress Plan (Post-Auth Refactor)

This document outlines the recommended steps to move the ICMP POC forward, focusing on testing and stability after the recent authentication and template handling refactoring.

See also:
*   [Auth/Template Refactor Summary](auth_template_refactor_summary.md)
*   [Database Schema](DATABASE_SCHEMA.md)
*   [API Specification](API_SPECIFICATION.md)
*   [Testing Strategy](TESTING_STRATEGY.md)

## Plan Steps

1.  **Manual DB Schema Verification & Update:**
    *   **Action:** Before running any tests or the application, manually verify and, if necessary, update your PostgreSQL database schema according to [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md):
        *   Rename the `prompt_templates` table to `default_templates`.
        *   Ensure the `stages` table has the correct JSONB columns (`stage_selection`, `data_extraction`, `response_generation`, `data_retrieval`) and `stage_selection_example_conversations` (TEXT).
    *   **Why:** Ensures the database matches the code's expectations, preventing immediate errors.

2.  **Review & Execute Mocked Backend Tests:**
    *   **Action:** Run the backend test suite (`pytest backend/tests`). Carefully review and debug the tests we created/updated, ensuring they pass:
        *   `test_auth.py`
        *   `test_save_config.py`
        *   `test_businesses.py`
        *   `test_stages.py`
        *   `test_conversations.py`
        *   `test_message_handling.py` (Pay close attention to mocks reflecting current logic).
    *   **Why:** Validates the refactored backend code logic in isolation using mocks, building confidence before integration.
    *   **Reference:** [Testing Strategy](TESTING_STRATEGY.md)

3.  **Basic Manual API Smoke Test:**
    *   **Action:** Start the backend server. Use an API client (e.g., Postman) to manually test the core flow against your development database (with the correct schema):
        *   `POST /businesses` (using master key via `Authorization: Bearer`) -> Get `business_id`, `api_key`.
        *   `POST /api/save-config` (using created IDs/key) -> Check for 200 OK and `businessApiKey` cookie.
        *   `GET /businesses/{business_id}` (with cookie) -> Check for 200 OK.
        *   `POST /stages` (with cookie, valid stage config JSON) -> Check for 201 Created.
        *   `POST /message` (with cookie, valid message data) -> Check for 200 OK and monitor logs.
    *   **Why:** Quick integration check of backend components and database interaction before involving the frontend.
    *   **Reference:** [API Specification](API_SPECIFICATION.md)

4.  **Debug Frontend Authentication/Interface Issues:**
    *   **Action:** Run the frontend (`npm start`). Systematically debug the reported frontend problems using browser developer tools (Network tab, Console):
        *   Verify `/api/save-config` request/response and cookie setting.
        *   Verify subsequent API calls include the `businessApiKey` cookie and check for errors (401, etc.).
    *   **Why:** Directly addresses user-facing issues by inspecting the frontend-backend communication layer.

5.  **Iterate & Refine:**
    *   **Action:** Based on frontend debugging (Step 4), fix frontend code (state, API calls, error handling).
    *   **Action:** Once the core flow is stable, proceed with implementing backend TODOs (e.g., stage selection logic in `message_handling.py`) or new features (e.g., User Authentication).
    *   **Why:** Incrementally build features and stability upon a verified foundation. 