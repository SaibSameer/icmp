# Testing Strategy

This document outlines the testing approach for the ICMP application.

## Frontend Testing (`/front-end`)

*   **Framework:** Jest (via Create React App scripts)
*   **Library:** React Testing Library (`@testing-library/react`)
*   **Assertions:** `@testing-library/jest-dom`

### Types of Tests

1.  **Unit Tests:** Test individual components or utility functions in isolation. Mock dependencies (child components, API calls, hooks).
2.  **Integration Tests:** Test the interaction between several components, often involving user events and state changes. Use `test-utils.js` for rendering with context if needed. Mock API calls using `jest.fn()` and `global.fetch`.
    *   Example: `front-end/src/components/__tests__/Configuration.test.js` tests the Configuration component, mocking `fetch`, `useNavigate`, and prop functions.
3.  **End-to-End (E2E) Tests:** (Future) Use tools like Cypress or Playwright to simulate user flows across the entire application (frontend + backend).

### Running Tests

```bash
cd front-end
npm test # or yarn test
```

### Mocking

*   **API Calls:** Mock `global.fetch` using `jest.fn()`, providing mock responses:
    ```javascript
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })
    );
    ```
*   **Modules/Hooks:** Use `jest.mock('module-name')`:
    ```javascript
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate, // mockNavigate is a jest.fn()
    }));
    ```

### Coverage

*   Run tests with coverage: `npm test -- --coverage`
*   [Specify coverage goals if any]

## Backend Testing (`/backend`)

*   **Framework:** Pytest
*   **Library:** Flask test client

### Types of Tests

1.  **Unit Tests:** Test individual functions, classes, or decorators in isolation. Mock database interactions and external API calls (OpenAI).
2.  **Integration Tests:** Test API endpoints using the Flask test client. This involves sending HTTP requests to the test application and asserting responses. Can use a test database.
    *   Example: `backend/tests/test_auth.py` tests authentication endpoints and decorators using the test client.

### Running Tests

```bash
cd backend
pytest # Ensure pytest is installed (add to requirements-dev.txt)
```

### Test Setup / Fixtures (Pytest)

*   Use fixtures (`@pytest.fixture`) to set up reusable test resources:
    *   Flask application instance (`app`).
    *   Flask test client (`client`).
    *   Database connection / Test database setup & teardown.
    *   Mocked external services.

### Mocking

*   Use `unittest.mock` (or `pytest-mock`) to patch functions/classes:
    *   Mock database functions (`db.get_db_connection`, `db.execute_query`).
    *   Mock OpenAI calls (`openai_helper.call_openai`).
    *   Mock Flask `current_app` configuration.

### Test Database

*   For integration tests, configure tests to use a separate test database to avoid interfering with development data.
*   Use fixtures to manage the creation, seeding, and dropping of the test database or tables around test runs.

### Coverage

*   Install `pytest-cov`: `pip install pytest-cov`
*   Run tests with coverage: `pytest --cov=./` (adjust path as needed)
*   [Specify coverage goals if any] 