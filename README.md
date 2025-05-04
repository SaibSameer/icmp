# ICMP Events API

## Overview

Intelligent Conversation Management Platform (ICMP) API for handling message processing, conversation management, and business logic, primarily driven by external messaging platform webhooks.

## Authentication

The system uses two main authentication methods:

1.  **Master API Key (`ICMP_API_KEY`):**
    *   Used for administrative API calls (e.g., creating businesses via `POST /businesses`).
    *   Set via the `ICMP_API_KEY` environment variable.
    *   Passed in the `Authorization: Bearer <key>` header.
    *   Validated by the `@require_api_key` decorator.

2.  **Webhook & Internal Key Authentication:**
    *   **Webhook Signature Verification:** Incoming webhooks (e.g., from Facebook) MUST be verified using platform-specific secrets (e.g., `FACEBOOK_APP_SECRET`) to ensure authenticity. See `backend/routes/message_handling.py`.
    *   **Internal API Key (`internal_api_key`):** Each business has a unique internal key generated during creation (`POST /businesses`). Webhook handlers retrieve this key after verifying the source and identifying the business.
    *   **Internal Authorization:** When webhook handlers or internal services call other backend API routes (e.g., `/api/stages`, `/api/conversations`), they pass the business's `internal_api_key` in the `Authorization: Bearer <internal_key>` header.
    *   **Validation:** Internal routes are protected by the `@require_internal_key` decorator, which validates the key and associates the request with the correct `business_id`.

**Note:** There is no direct user login or session management for business-specific operations via the API. Authentication is handled at the webhook source and internally via API keys.

Refer to `AUTH_GUIDELINES.md` for more details.

## Setup & Installation

### Prerequisites
- Python 3.x
- pip
- PostgreSQL
- Access to OpenAI API
- Platform App Secrets (e.g., Facebook App Secret for webhook verification)

### Local Setup

1.  **Clone Repository:** `git clone ...`
2.  **Create Virtual Environment:** `python -m venv venv` and activate it.
3.  **Install Dependencies:** `pip install -r requirements.txt` (ensure `PyJWT` and potentially `hmac`, `hashlib` are included if not built-in).
4.  **Environment Variables:** Create a `.env` file in the project root (or `backend/` directory, check `run_local.py`). Copy `.env.example` and fill in your database credentials, `FLASK_SECRET_KEY`, `ICMP_API_KEY`, `OPENAI_API_KEY`, and platform secrets (`FACEBOOK_APP_SECRET`, etc.).
5.  **Database Setup:** Ensure PostgreSQL is running. Run `python setup_database.py` to create tables based on `database_setup.sql`.
6.  **Run Backend:** `python run_local.py` (starts Flask dev server, usually on port 5000).

### Deployment (Example: Render)

1.  Use `render.yaml` for configuration.
2.  Ensure all required environment variables (DB credentials, API keys, secrets) are set in the Render service configuration.
3.  Build command likely involves `pip install`.
4.  Start command typically uses `gunicorn` (e.g., `gunicorn backend.app:app`).

## Project Structure

```
/
├── backend/            # Flask application
│   ├── routes/         # API route handlers (Blueprints)
│   ├── schemas/        # JSON schemas
│   ├── tests/          # Pytest tests
│   ├── app.py          # Flask app creation and configuration
│   ├── auth.py         # Authentication decorators (@require_api_key, @require_internal_key)
│   ├── config.py       # Config loading
│   ├── db.py           # Database connection handling
│   └── ...
├── frontend/           # React frontend (if used, likely for admin)
│   └── ... 
├── .env.example        # Example environment variables
├── .gitignore
├── AUTH_GUIDELINES.md  # Detailed authentication explanation
├── database_setup.sql  # Database schema
├── requirements.txt    # Python dependencies
├── run_local.py        # Script to run backend locally
├── setup_database.py   # Script to setup database tables
├── README.md           # This file
└── ...
```

## Usage

1.  **Create a Business:** Make a `POST` request to `/businesses` with required data, authenticated using the Master API Key (`ICMP_API_KEY`). Note the returned `business_id` and `internal_api_key`.
2.  **Configure Webhook:** Set up webhooks on the external platform (e.g., Facebook) pointing to your deployed `/webhooks/facebook` endpoint. Configure the necessary verification token and ensure the platform secret (`FACEBOOK_APP_SECRET`) matches your backend environment variable.
3.  **Map Platform ID:** Ensure your backend has a way to map the platform identifier (e.g., Page ID) received in the webhook to the correct `business_id` to retrieve the `internal_api_key`.
4.  **Send Messages:** Messages sent via the configured platform will trigger the webhook, initiating the processing flow.

## Testing

- Run backend tests using `pytest` from the `backend/` directory.
- Tests need to be updated to mock the new authentication decorators and provide appropriate `Authorization` headers.