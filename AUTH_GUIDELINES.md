# Authentication Guidelines (for AI Assistants & Developers)

This document outlines the authentication mechanisms used in the ICMP project.

**Current Model (Webhook-Centric):** The primary interaction with the system is expected via webhooks from external messaging platforms (e.g., Facebook Messenger, WhatsApp). Direct user UI access is not the main focus. Authentication relies on verifying the webhook source and using internal API keys.

Ref: See `backend/documentation/auth_template_refactor_summary.md` for history of previous (now removed) authentication models.

## 1. Master API Key (`ICMP_API_KEY`)

*   **Purpose:** Administrative tasks via direct API calls (e.g., creating businesses, managing global settings or templates). **Not** used by webhooks or regular message processing.
*   **Source:** Loaded from environment variables on the backend (`.env` file -> `backend/config.py`). Should **never** be exposed publicly.
*   **Usage:** Pass this key in the `Authorization` header as a Bearer token.
    ```
    Authorization: Bearer <your_ICMP_API_KEY>
    ```
*   **Validation:** Checked by the `@require_api_key` decorator in `backend/auth.py`.

## 2. Webhook Authentication & Authorization

This is the primary flow for processing messages from external platforms.

*   **Step 1: Webhook Signature Verification (Essential)**
    *   **Purpose:** To verify that an incoming request to a webhook endpoint (e.g., `/webhooks/facebook`) genuinely originates from the expected platform (e.g., Facebook) and not a malicious actor.
    *   **Mechanism:** Each platform has its own method, typically involving a shared secret (e.g., Facebook App Secret) configured on both the platform and in the backend (`.env` file). The platform signs the request payload, and the webhook handler uses the secret to verify the signature (e.g., using `hmac`).
    *   **Implementation:** See webhook handlers in `backend/routes/message_handling.py` (or similar) for platform-specific verification logic (e.g., `verify_facebook_signature`). **This step must be performed before processing any payload data.**

*   **Step 2: Business Identification & Internal API Key Retrieval**
    *   **Purpose:** To map the incoming verified webhook request to the correct internal business context.
    *   **Mechanism:** The webhook handler extracts platform-specific identifiers from the verified payload (e.g., Facebook Page ID, WhatsApp Business Number). It uses these identifiers to look up the corresponding `business_id` and its associated `internal_api_key` from the `businesses` database table.
    *   **Internal API Key:** This key is generated securely (using `secrets.token_hex()`) when a business is created (via `POST /businesses`, protected by the Master API Key) and stored in the `businesses.internal_api_key` column. It acts as a pre-shared secret for internal authorization.

*   **Step 3: Internal API Call Authorization**
    *   **Purpose:** To authorize the webhook handler process to access internal backend routes/services (e.g., fetching stages, conversations, calling LLMs) on behalf of the identified business.
    *   **Mechanism:** When the webhook handler needs to call another internal API endpoint or service function, it includes the retrieved `internal_api_key` in the `Authorization` header.
        ```
        Authorization: Bearer <internal_api_key_for_the_business>
        ```
    *   **Validation:** Internal routes (e.g., in `stages.py`, `conversations.py`) are protected by the `@require_internal_key` decorator (`backend/auth.py`). This decorator extracts the key from the Bearer token, verifies it exists in the `businesses.internal_api_key` column, and attaches the corresponding `business_id` to `flask.g` for the route to use.

## Key Files

*   `backend/auth.py`: Contains `@require_api_key` and `@require_internal_key` decorators.
*   `backend/routes/message_handling.py` (or similar): Contains webhook handlers implementing signature verification and internal key usage.
*   `backend/routes/businesses.py`: Contains `POST /businesses` (protected by `@require_api_key`) which generates `internal_api_key`.
*   `backend/routes/stages.py`, `conversations.py`, etc.: Internal routes protected by `@require_internal_key`.
*   `.env.example`: Shows required environment variables including `ICMP_API_KEY` and platform secrets (e.g., `FACEBOOK_APP_SECRET`).
*   `database_setup.sql`: Defines the `businesses` table including `internal_api_key`.

## Important Considerations

*   **Signature Verification is Crucial:** Never process webhook payloads without first verifying the platform's signature.
*   **Secret Management:** Keep platform secrets (`FACEBOOK_APP_SECRET`, etc.) and the `ICMP_API_KEY` secure (use environment variables, not hardcoding).
*   **Business Mapping:** Ensure a reliable way to map incoming webhook identifiers (Page ID, phone number) to the internal `business_id`.
*   **Internal Key Security:** The `internal_api_key` should be treated as sensitive. It's generated once and used internally. Ensure it's stored securely in the database.
*   **Frontend:** If a frontend exists, it's likely for administrative purposes only, authenticated using the Master API Key (`@require_api_key`). Code related to user login via business keys/cookies should be removed.