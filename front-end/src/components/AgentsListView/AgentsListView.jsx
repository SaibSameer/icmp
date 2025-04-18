import React, { useState, useEffect } from 'react';
// Import useNavigate from react-router-dom
import { useNavigate } from 'react-router-dom';

// Define your backend API base URL
const API_BASE_URL = 'http://localhost:5000';

function AgentsListView() {
    const [agents, setAgents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    // Initialize useNavigate hook
    const navigate = useNavigate();

    // TODO: Replace with actual business ID from context/props/state management
    const businessId = '7ae167a0-d864-43b9-bdaf-fcba35b33f27'; // Replace with a REAL ID for testing

    useEffect(() => {
        const fetchAgents = async () => {
            if (!businessId || businessId === 'YOUR_BUSINESS_ID_HERE') {
                setError("Business ID not available.");
                setIsLoading(false);
                return;
            }
            setIsLoading(true);
            setError(null);
            console.log(`Fetching agents for business ID: ${businessId}`);

            try {
                const response = await fetch(`${API_BASE_URL}/agents?business_id=${businessId}`, {
                    method: 'GET',
                    credentials: 'include', // Send cookies
                    headers: {
                        'Accept': 'application/json',
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(`HTTP error ${response.status}: ${errorData.message || 'Failed to fetch agents'}`);
                }

                const fetchedAgents = await response.json();
                setAgents(fetchedAgents);

            } catch (err) {
                console.error("Error fetching agents:", err);
                setError(err.message || "An unexpected error occurred while fetching agents.");
                setAgents([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAgents();

    }, [businessId]);

    // Implement navigation to stages view with agent_id parameter
    const handleManageStages = (agentId) => {
        console.log(`Navigate to manage stages for agent: ${agentId === null ? 'General' : agentId}`);
        // Navigate to the StageManager with agent_id and business_id query parameters
        navigate(`/stages?business_id=${businessId}&agent_id=${agentId === null ? '' : agentId}`);
    };

    // Add function to delete an agent
    const handleDeleteAgent = async (agentId, agentName) => {
        if (!window.confirm(`Are you sure you want to delete agent "${agentName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/agents/${agentId}?business_id=${businessId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ business_id: businessId })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.message || 'Failed to delete agent'}`);
            }

            // Success! Remove the agent from the list
            setAgents(prevAgents => prevAgents.filter(agent => agent.agent_id !== agentId));
            alert(`Agent "${agentName}" deleted successfully.`);
        } catch (err) {
            console.error("Error deleting agent:", err);
            alert(`Error deleting agent: ${err.message}`);
        }
    };

    if (isLoading) {
        return <div>Loading agents...</div>;
    }

    if (error) {
        return <div style={{ color: 'red' }}>Error: {error}</div>;
    }

    return (
        <div>
            <h2>Manage Agents & Stages</h2>
            <p>Select an agent or manage general stages.</p>
             {/* TODO: Add button/link to create new agents later */}

            {/* General Stages Option */}
            <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                <h3>General Stages</h3>
                <p>Manage stages that apply to all agents.</p>
                <button onClick={() => handleManageStages(null)}>
                    Manage General Stages
                </button>
            </div>

            <hr />

             <h3>Specific Agents</h3>
            {agents.length > 0 ? (
                agents.map(agent => (
                    <div key={agent.agent_id} style={{ border: '1px solid #eee', padding: '10px', marginBottom: '10px' }}>
                        <h4>{agent.agent_name}</h4>
                        <p>Role: {agent.agent_role || 'N/A'}</p>
                        <p>ID: {agent.agent_id}</p>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button onClick={() => handleManageStages(agent.agent_id)}>
                                Manage Stages for {agent.agent_name}
                            </button>
                            <button 
                                onClick={() => handleDeleteAgent(agent.agent_id, agent.agent_name)}
                                style={{ backgroundColor: '#f44336', color: 'white' }}
                            >
                                Delete Agent
                            </button>
                        </div>
                    </div>
                ))
            ) : (
                <p>No specific agents found for this business.</p>
            )}
        </div>
    );
}

export default AgentsListView;