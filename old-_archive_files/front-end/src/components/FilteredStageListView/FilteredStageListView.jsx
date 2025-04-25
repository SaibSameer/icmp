import React, { useState, useEffect } from 'react';
// Import routing hooks
import { useLocation, useNavigate } from 'react-router-dom';

// Define your backend API base URL
const API_BASE_URL = 'http://localhost:5000';

function FilteredStageListView() {
    const [stages, setStages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [contextAgentId, setContextAgentId] = useState(null); // agent_id or 'null' for general
    const [contextAgentName, setContextAgentName] = useState('General'); // For display
    const navigate = useNavigate();
    const location = useLocation();

    // Get business and agent ID from query params
    const queryParams = new URLSearchParams(location.search);
    const businessId = queryParams.get('business_id') || localStorage.getItem('businessId');
    const agentIdParam = queryParams.get('agent_id') || '';
    
    // Fetch agent details when agent_id is available
    useEffect(() => {
        const fetchAgentDetails = async () => {
            if (!agentIdParam || agentIdParam === 'null' || agentIdParam === '') {
                setContextAgentId('');
                setContextAgentName('General');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/agents/${agentIdParam}?business_id=${businessId}`, {
                    credentials: 'include'
                });
                
                if (!response.ok) {
                    throw new Error('Failed to fetch agent details');
                }
                
                const agentData = await response.json();
                setContextAgentId(agentIdParam);
                setContextAgentName(agentData.agent_name || `Agent ${agentIdParam}`);
            } catch (err) {
                console.error("Error fetching agent details:", err);
                setContextAgentId(agentIdParam);
                setContextAgentName(`Agent ${agentIdParam}`); // Fallback
            }
        };
        
        fetchAgentDetails();
    }, [agentIdParam, businessId]);

    // Fetch stages when businessId or contextAgentId is determined
    useEffect(() => {
        const fetchStages = async () => {
            if (!businessId) { 
                 setError("Business ID not available.");
                 setIsLoading(false);
                 return;
            }

            setIsLoading(true);
            setError(null);
            console.log(`Fetching stages for business ID: ${businessId}, Agent Context: ${contextAgentId || 'General'}`);

            // Construct the URL with the agent_id filter
            let url = `${API_BASE_URL}/stages?business_id=${businessId}`;
            if (contextAgentId) {
                url += `&agent_id=${contextAgentId}`;
            }

            try {
                const response = await fetch(url, {
                    method: 'GET',
                    credentials: 'include', // Send cookies
                    headers: {
                        'Accept': 'application/json',
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(`HTTP error ${response.status}: ${errorData.message || 'Failed to fetch stages'}`);
                }

                const fetchedStages = await response.json();
                setStages(fetchedStages);

            } catch (err) {
                console.error("Error fetching stages:", err);
                setError(err.message || "An unexpected error occurred while fetching stages.");
                setStages([]);
            } finally {
                setIsLoading(false);
            }
        };

        if (businessId) {
            fetchStages();
        }

    }, [businessId, contextAgentId]); // Refetch if business or agent context changes

    const handleAddStage = () => {
        console.log(`Navigate to Add Stage form for agent context: ${contextAgentId}`);
         // TODO: Use navigate to go to the Add/Edit Stage form, passing context
         // Example: navigate(`/stages/new?agent_id=${contextAgentId}`);
    };

    const handleEditStage = (stageId) => {
        console.log(`Navigate to Edit Stage form for stage: ${stageId}, agent context: ${contextAgentId}`);
        // TODO: Use navigate
        // Example: navigate(`/stages/edit/${stageId}?agent_id=${contextAgentId}`);
    };

    const handleDeleteStage = async (stageId, stageName) => {
        if (!window.confirm(`Are you sure you want to delete the stage "${stageName}"?`)) {
            return;
        }

        console.log(`Deleting stage: ${stageId} with businessId: ${businessId}`);
        setError(null); // Clear previous errors

        try {
             // Make sure we have a business ID
             if (!businessId) {
                 throw new Error("Business ID is required for deletion");
             }
             
             // Get the business API key from localStorage for authorization
             const businessApiKey = localStorage.getItem('businessApiKey');
             if (!businessApiKey) {
                 throw new Error("Business API Key is required for deletion");
             }
             
             // Note: DELETE request needs business_id in query args or body for the backend endpoint
             const deleteUrl = `${API_BASE_URL}/stages/${stageId}?business_id=${businessId}`;
             console.log(`Making DELETE request to: ${deleteUrl}`);
             
             const response = await fetch(deleteUrl, {
                 method: 'DELETE',
                 credentials: 'include',
                 headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${businessApiKey}`
                 }
             });

             console.log(`Delete response status: ${response.status}`);
             
             // Handle response based on status code
             if (response.status === 204) {
                // 204 No Content is a success response for DELETE
                console.log(`Stage ${stageId} deleted successfully with 204 response.`);
                // Remove stage from local state
                setStages(prevStages => prevStages.filter(s => s.stage_id !== stageId));
                return; // Exit successfully
             } else if (response.status === 200) {
                // Some APIs return 200 OK for successful DELETE
                console.log(`Stage ${stageId} deleted successfully with 200 response.`);
                // Remove stage from local state
                setStages(prevStages => prevStages.filter(s => s.stage_id !== stageId));
                return; // Exit successfully
             } else if (!response.ok) {
                // Try to get error details from response body
                const errorText = await response.text();
                console.error(`Failed to delete stage. Status: ${response.status}, Response: ${errorText}`);
                
                try {
                    const errorData = JSON.parse(errorText);
                    throw new Error(`Failed to delete stage: ${errorData.error || errorData.message || 'Unknown error'}`);
                } catch (parseError) {
                    throw new Error(`Failed to delete stage: HTTP error ${response.status}`);
                }
             }

        } catch (err) {
             console.error("Error deleting stage:", err);
             setError(err.message || "An unexpected error occurred while deleting the stage.");
        }
    };


    if (isLoading) {
        return <div>Loading stages for {contextAgentName}...</div>;
    }

    // Display error prominently
    if (error) {
        return <div style={{ color: 'red' }}>Error: {error}</div>;
    }

    return (
        <div>
            {/* Display which agent context we are viewing */}
            <h2>Manage Stages for: {contextAgentName}</h2>

            {/* Add New Stage Button */}
            {/* TODO: Use Link or navigate onClick */}
            <button onClick={handleAddStage} style={{ marginBottom: '15px' }}>
                Add New Stage
            </button>

             {/* TODO: Improve table styling */}
            <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Created At</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {stages.length > 0 ? (
                        stages.map(stage => (
                            <tr key={stage.stage_id}>
                                <td>{stage.stage_name}</td>
                                <td>{stage.stage_type}</td>
                                <td>{stage.stage_description}</td>
                                <td>{new Date(stage.created_at).toLocaleString()}</td>
                                <td>
                                     {/* TODO: Use Link or navigate onClick */}
                                    <button onClick={() => handleEditStage(stage.stage_id)} style={{ marginRight: '5px' }}>
                                        Edit
                                    </button>
                                    <button onClick={() => handleDeleteStage(stage.stage_id, stage.stage_name)}>
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5" style={{ textAlign: 'center' }}>No stages found for this context.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default FilteredStageListView;