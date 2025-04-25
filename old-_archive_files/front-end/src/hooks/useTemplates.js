import { useState, useEffect, useCallback } from 'react';
import { fetchTemplates } from '../services/templateService';
import useConfig from './useConfig';
import { normalizeUUID } from './useConfig';

const useTemplates = (handleSnackbarOpen, agentId) => {
    const [templates, setTemplates] = useState([]); // Initialize as empty array
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const { businessId } = useConfig(); // Get businessId from config
    const normalizedBusinessId = normalizeUUID(businessId);
    const normalizedAgentId = normalizeUUID(agentId);

    const fetchTemplatesData = useCallback(async () => {
        if (!normalizedBusinessId || !normalizedAgentId) {
            setTemplates([]); // Clear templates if no businessId or agentId
            return;
        }

        setIsLoading(true);
        setError(null);
        console.log(`Fetching templates for business ID: ${normalizedBusinessId}, agent ID: ${normalizedAgentId}`);

        try {
            // Fetch templates from the API
            const data = await fetchTemplates(normalizedBusinessId, normalizedAgentId);
            console.log("Fetched templates:", data);
            // Ensure data is always an array, even if API returns null/undefined
            setTemplates(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error("Error fetching templates:", err);
            const errorMessage = err.message || 'Failed to fetch templates';
            setError(errorMessage);
            setTemplates([]); // Clear templates on error
            if (handleSnackbarOpen) {
                // Use the extracted error message for the snackbar
                handleSnackbarOpen(`Error fetching templates: ${errorMessage}`, "error");
            }
        } finally {
            setIsLoading(false);
        }
    }, [normalizedBusinessId, normalizedAgentId, handleSnackbarOpen]);

    // useEffect to trigger fetch when businessId or agentId changes
    useEffect(() => {
        fetchTemplatesData();
    }, [fetchTemplatesData]); // Dependency array includes fetchTemplatesData (memoized via useCallback)

    return {
        templates,       // The array of template objects
        isLoading,       // Boolean indicating if fetch is in progress
        error,           // Error object/message if fetch failed
        refreshTemplates: fetchTemplatesData // Function to manually trigger a refresh
    };
};

export default useTemplates;