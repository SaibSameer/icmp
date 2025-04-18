import { useState, useEffect, useCallback } from 'react';
// Assuming an agentService.js file will export fetchAgents
// We might need to create/update this service file later
import { fetchAgents } from '../services/agentService';
import useConfig from './useConfig';
import { normalizeUUID } from './useConfig';

const useAgents = (handleSnackbarOpen) => {
    const [agents, setAgents] = useState([]); // Initialize as empty array
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const { businessId } = useConfig(); // Get businessId from config
    const normalizedBusinessId = normalizeUUID(businessId);

    const fetchAgentsData = useCallback(async () => {
        if (!normalizedBusinessId) {
            setAgents([]); // Clear agents if no businessId
            return;
        }

        setIsLoading(true);
        setError(null);
        console.log(`Fetching agents for business ID: ${normalizedBusinessId}`);

        try {
            // Fetch agents from the API
            const data = await fetchAgents(normalizedBusinessId);
            console.log("Fetched agents:", data);
            // Ensure data is always an array, even if API returns null/undefined
            setAgents(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error("Error fetching agents:", err);
            const errorMessage = err.message || 'Failed to fetch agents';
            setError(errorMessage);
            setAgents([]); // Clear agents on error
             if (handleSnackbarOpen) {
                // Use the extracted error message for the snackbar
                handleSnackbarOpen(`Error fetching agents: ${errorMessage}`, "error");
            }
        } finally {
            setIsLoading(false);
        }
    }, [normalizedBusinessId, handleSnackbarOpen]);

    // useEffect to trigger fetch when businessId changes
    useEffect(() => {
        fetchAgentsData();
    }, [fetchAgentsData]); // Dependency array includes fetchAgents (memoized via useCallback)

    return {
        agents,          // The array of agent objects
        isLoading,       // Boolean indicating if fetch is in progress
        error,           // Error object/message if fetch failed
        refreshAgents: fetchAgentsData // Function to manually trigger a refresh
    };
};

export default useAgents;