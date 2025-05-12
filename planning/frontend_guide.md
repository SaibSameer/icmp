# Frontend Guide (React)

This guide provides details specific to the `/front-end` React application.

## Technology Stack

*   **Framework:** React
*   **UI Library:** Material UI (MUI) v5
*   **Routing:** `react-router-dom` v6
*   **Language:** JavaScript (with JSX)
*   **Package Manager:** npm (or yarn, specify in README)
*   **API Calls:** Browser `fetch` API

## Project Structure (`/src`)

*   **`components/`:** Reusable UI components
    - `StageView.jsx`: Displays stage details in read-only mode
    - `StageManager.js`: Manages the list of stages and stage operations
    - `StageEditor.js`: Form for creating/editing stages
    - Other common components (Buttons, TextFields, etc.)
*   **`pages/`:** Top-level components representing application pages/views
    - `StageViewPage.jsx`: Page wrapper for stage view
    - `StageEditorPage.js`: Page wrapper for stage editor
*   **`contexts/`:** React context providers for state management
*   **`hooks/`:** Custom React hooks
*   **`services/`:** API call modules
    - `stageService.js`: Stage-related API calls
    - Other service modules
*   **`utils/`:** Utility functions
*   **`App.js`:** Main application component, sets up routing
*   **`index.js`:** Application entry point
*   **`test-utils.js`:** Testing utilities

## State Management

*   Currently uses prop drilling and local component state (useState)
*   **Recommendation:** Consider using:
    - React Context API for shared state
    - Zustand or Redux Toolkit for complex state

## Routing

*   Managed by `react-router-dom`
*   Key routes defined in `App.js`:
    ```javascript
    <Routes>
      <Route path="/stages" element={<StageManager />} />
      <Route path="/stages/:stageId" element={<StageViewPage />} />
      <Route path="/stage-editor/:stageId" element={<StageEditorPage />} />
      <Route path="/stage-editor/new" element={<StageEditorPage />} />
      {/* Other routes */}
    </Routes>
    ```

## API Interaction

*   Uses the browser's `fetch` API.
*   **Authentication:** Relies primarily on the `businessApiKey` which is set as a secure, `HttpOnly` **cookie** by the backend `/api/save-config` endpoint after successful configuration via `Configuration.js`.
    *   API calls using `fetch` should include `credentials: 'include'` in their options to ensure the browser sends the authentication cookie.
    *   The backend decorator (`@require_business_api_key`) validates this cookie along with the `business_id` associated with the request.
*   **Getting `business_id` for API calls:** Once configured, the application should store the active `business_id` in its state (e.g., React Context or component state). API service functions (like `stageService.getStage`) should receive the `business_id` from this state, rather than relying on `localStorage` as shown in some older examples.
*   **Error Handling:** Checks `response.ok` and handles errors appropriately.

Example service module structure (ensure `credentials: 'include'` is set):
```javascript
// src/services/stageService.js
const API_BASE_URL = '/api';

async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        credentials: 'include', // Ensure cookies are sent
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const error = new Error(errorData?.message || `HTTP error ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
    }

    return response.status === 204 ? null : response.json();
}

// Stage-related API calls
export const stageService = {
    getStages: (businessId, agentId) => {
        const params = new URLSearchParams({ business_id: businessId });
        if (agentId) params.append('agent_id', agentId);
        return request(`/stages?${params}`);
    },

    getStage: (stageId, businessId) => {
        return request(`/stages/${stageId}?business_id=${businessId}`);
    },

    createStage: (stageData) => {
        return request('/stages', {
            method: 'POST',
            body: JSON.stringify(stageData),
        });
    },

    updateStage: (stageId, stageData) => {
        return request(`/stages/${stageId}`, {
            method: 'PUT',
            body: JSON.stringify(stageData),
        });
    },

    deleteStage: (stageId, businessId) => {
        return request(`/stages/${stageId}?business_id=${businessId}`, {
            method: 'DELETE',
        });
    },
};
```

## Key Components

### StageView Component (Conceptual Update)

```jsx
// src/components/StageView.jsx - Conceptual Example
import React, { useState, useEffect, useContext } from 'react'; // Assuming context for businessId
// import { AppContext } from '../contexts/AppContext'; // Example context

function StageView({ stageId }) {
    // const { businessId } = useContext(AppContext); // Get businessId from context/state
    const [stageData, setStageData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const businessId = "get-from-state-or-context"; // Placeholder

    useEffect(() => {
        if (!businessId) {
            setError("Business not configured.");
            setLoading(false);
            return;
        }
        const fetchStage = async () => {
            try {
                // Pass businessId obtained from state/context
                const data = await stageService.getStage(stageId, businessId);
                setStageData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchStage();
    }, [stageId, businessId]);

    // Render loading, error, or stage data
    // ... (render logic) ...
}
```
*Note: The example above is conceptual. The actual implementation might differ, but it illustrates obtaining `businessId` from application state rather than `localStorage` for API calls.* 

### StageManager Component

```jsx
// src/components/StageManager.js
function StageManager() {
    const [stages, setStages] = useState([]);
    const navigate = useNavigate();

    const handleStageClick = (stageId) => {
        navigate(`/stages/${stageId}`);
    };

    const handleEditClick = (stageId, event) => {
        event.stopPropagation();
        navigate(`/stage-editor/${stageId}`);
    };

    return (
        <Container>
            <StageList 
                stages={stages} 
                onStageClick={handleStageClick}
                onEditClick={handleEditClick}
            />
        </Container>
    );
}
```

## Building for Production

```bash
npm run build # or yarn build
```
Creates an optimized build in `build/` directory.

## Testing

*   Use React Testing Library for component tests
*   Mock API calls in tests using `jest.mock`
*   Example test:
    ```javascript
    // src/components/__tests__/StageView.test.js
    import { render, screen, waitFor } from '@testing-library/react';
    import StageView from '../StageView';
    import { stageService } from '../../services/stageService';

    jest.mock('../../services/stageService');

    describe('StageView', () => {
        it('displays stage details when loaded', async () => {
            const mockStage = {
                stage_name: 'Test Stage',
                stage_description: 'Test Description',
                // ... other fields
            };
            stageService.getStage.mockResolvedValue(mockStage);

            render(<StageView stageId="test-id" />);

            await waitFor(() => {
                expect(screen.getByText('Test Stage')).toBeInTheDocument();
                expect(screen.getByText('Test Description')).toBeInTheDocument();
            });
        });
    });
    ```

## Key Components

*   **`Configuration.js`:** Handles user input for `userId`, `businessId`, and the `businessApiKey` obtained after business creation. It calls the backend `/api/save-config` endpoint, which validates these details and, upon success, sets the `businessApiKey` HttpOnly cookie required for subsequent API calls.
*   *(Add descriptions of other major components as they are developed)* 

## Related Documentation
- See [API Documentation](api_documentation.md) for endpoint details
- See [Implementation Guide](implementation_guide.md) for system architecture
- See [Development Roadmap](development_roadmap.md) for project timeline

Last Updated: 2025-05-12
