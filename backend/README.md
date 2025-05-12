# ICMP - Intelligent Conversation Management Platform

## Project Overview

The ICMP POC aims to automate and enhance customer interactions for businesses using a scalable, multi-agent, context-aware conversation system powered by Large Language Models (LLMs).

See [Project Summary](c:\icmp_events_api\archive_output\project_archive\sumary.txt) or [Full Implementation Guide (Draft)](documentation/100%.txt) for more details.

**Current Status:** Proof of Concept (POC) - Core features partially implemented, ongoing refactoring (See [Auth/Template Summary](documentation/auth_template_refactor_summary.md)). Test suite: 45/51 tests passing, with ongoing fixes for business and conversation route tests.

## Quick Start / Setup

### Prerequisites

*   Python Version: [Specify Version, e.g., 3.10+]
*   Node.js Version: [Specify Version, e.g., 18+]
*   npm/yarn: [Specify Version]
*   PostgreSQL Version: [Specify Version, e.g., 14+]
*   Access to OpenAI API

### Backend Setup (`/backend` directory)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Environment Variables:** Create a `.env` file in the `backend` directory with the following variables:
    ```dotenv
    DB_NAME=icmp_db
    DB_USER=icmp_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    OPENAI_API_KEY=your_openai_key
    ICMP_API_KEY=generate_a_strong_secret_key # Master key for admin/server tasks (e.g., passed via Authorization: Bearer header)
    # Add other variables as needed (e.g., for Flask secret key)
    FLASK_SECRET_KEY=generate_another_strong_secret
    # NOTE: The businessApiKey is generated per business and handled via HttpOnly cookie, not set here.
    ```
3.  **Database Setup:**
    *   Ensure PostgreSQL is running.
    *   Create the database user and database specified in `.env`.
    *   Apply the necessary table schemas. **Note:** The canonical `CREATE TABLE` statements need consolidation (see [Database Schema Doc](documentation/DATABASE_SCHEMA.md) or `documentation/100%.txt`). The `prompt_templates` table has been deprecated and replaced by the new `templates` table. Ensure the `stages` table has the correct foreign key references to the `templates` table.
    *   [Add specific commands/migration steps here if they exist, e.g., `flask db upgrade`]
4.  **Run Backend Server:**
    ```bash
    flask run # Or python app.py
    ```
    The server should be running on `http://localhost:5000`.

### Frontend Setup (`/front-end` directory)

1.  **Install Dependencies:**
    ```bash
    cd front-end
    npm install # or yarn install
    ```
2.  **Run Frontend Dev Server:**
    ```bash
    npm start # or yarn start
    ```
    The frontend should be accessible at `http://localhost:3000`.

## Directory Structure

```
/backend
├── api/            # API version management and endpoints
├── core/           # Core functionality and error handling
├── database/       # Database management and operations
├── message_processing/  # Message handling and processing
├── routes/         # API route handlers (Blueprints)
├── schemas/        # JSON schemas for validation
├── services/       # Service layer implementation
├── template_management/  # Template management and organization
├── tests/          # Test suite and test utilities
├── tools/          # Diagnostic and utility scripts
├── utils/          # Utility functions and helpers
├── app.py          # Main Flask application
├── auth.py         # Authentication decorators
├── config.py       # Configuration loading
├── db.py           # Database connection handling
├── requirements.txt # Backend dependencies
├── .env            # Environment variables (local only)
└── ...
/front-end
├── public/
├── src/
│   ├── components/ # React components
│   ├── pages/      # Page-level components
│   ├── services/   # API call functions
│   ├── App.js      # Main application component
│   └── index.js    # Entry point
├── package.json    # Frontend dependencies
└── ...
README.md           # This file
```

## Further Documentation

*   [API Specification](documentation/API_SPECIFICATION.md)
*   [Database Schema](documentation/DATABASE_SCHEMA.md)
*   [Core Logic Explained](documentation/CORE_LOGIC_EXPLAINED.md)
*   [Architecture Overview](documentation/ARCHITECTURE.md)
*   [Frontend Guide](documentation/FRONTEND_GUIDE.md)
*   [Testing Strategy](documentation/TESTING_STRATEGY.md)
*   [Auth/Template Refactor Summary](documentation/auth_template_refactor_summary.md)

## Testing

The project includes a comprehensive test suite using pytest. To run the tests:

```bash
cd backend
pytest
```

### Test Coverage
- Authentication and authorization tests
- Business management route tests
- Conversation handling tests
- Message processing tests
- Database interaction tests

### Known Issues
- Some tests in the business routes are currently failing and being addressed
- Conversation route tests need updates to match the latest API changes
- Authentication tests are being updated to handle standardized error responses 

## Authentication

This project uses two primary authentication methods:

1.  **Master API Key (`ICMP_API_KEY`):** Set in the `.env` file. Used for administrative actions and server-to-server communication. Typically passed via the `Authorization: Bearer <key>` header. See `@require_api_key` in `backend/auth.py`.
2.  **Business API Key (`businessApiKey`):** Generated when a business is created. Handled via a secure `HttpOnly` cookie set by the `/api/save-config` endpoint after frontend configuration. Used for authenticating requests related to specific business data. See `@require_business_api_key` in `backend/auth.py`.

Refer to `AUTH_GUIDELINES.md` for detailed usage. 