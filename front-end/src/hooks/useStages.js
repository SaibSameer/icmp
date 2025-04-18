// src/hooks/useStages.js
import { useState, useEffect, useCallback } from 'react';
// Assuming a stageService.js file will export fetchStages
// We might need to create/update this service file later
import { fetchStages as fetchStagesApi } from '../services/stageService';

// This hook takes the selectedAgentId as an argument
const useStages = (selectedAgentId, handleSnackbarOpen) => {
    const [stages, setStages] = useState([]); // Initialize as empty array
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchStages = useCallback(async () => {
        // Only fetch if an agent is selected
        if (!selectedAgentId) {
            setStages([]); // Clear stages if no agent is selected
            return;
        }

        setIsLoading(true);
        setError(null);
        console.log(`Fetching stages for agent ID: ${selectedAgentId}`);

        try {
            // API key relies on httpOnly cookie sent automatically by browser
            const data = await fetchStagesApi(selectedAgentId);
            console.log("Fetched stages:", data);
            // Ensure data is always an array
            setStages(Array.isArray(data) ? data : []);
            // Optional: Snackbar notification
            // if (handleSnackbarOpen) {
            //      handleSnackbarOpen("Stages loaded!", "info");
            // }
        } catch (err) {
            console.error("Error fetching stages:", err);
            const errorMessage = err.message || 'Failed to fetch stages';
            setError(errorMessage);
            setStages([]); // Clear stages on error
             if (handleSnackbarOpen) {
                handleSnackbarOpen(`Error fetching stages: ${errorMessage}`, "error");
            }
        } finally {
            setIsLoading(false);
        }
    }, [selectedAgentId, handleSnackbarOpen]); // Depend on selectedAgentId

    // useEffect to trigger fetch when selectedAgentId changes
    useEffect(() => {
        fetchStages();
    }, [fetchStages]); // Dependency array includes fetchStages (memoized by useCallback)

    return {
        stages,          // The array of stage objects
        isLoading,       // Boolean indicating if fetch is in progress
        error,           // Error object/message if fetch failed
        refreshStages: fetchStages // Function to manually trigger a refresh
    };
};

export default useStages;