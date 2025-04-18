import { useState, useEffect, useCallback } from 'react';
// Assuming a stageService.js file will export fetchStageDetails
// We might need to create/update this service file later
import { fetchStageDetails as fetchStageDetailsApi } from '../services/stageService';

// This hook takes the stageId to fetch details for
const useStageDetails = (stageId, handleSnackbarOpen) => {
    const [stageDetails, setStageDetails] = useState(null); // Initialize as null
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchDetails = useCallback(async () => {
        // Only fetch if a stage ID is provided
        if (!stageId) {
            setStageDetails(null); // Clear details if no stageId
            return;
        }

        setIsLoading(true);
        setError(null);
        console.log(`Fetching details for stage ID: ${stageId}`);

        try {
            // API key relies on httpOnly cookie
            const data = await fetchStageDetailsApi(stageId);
            console.log("Fetched stage details:", data);
            setStageDetails(data); // Store the fetched object
            // Optional: Snackbar notification
            // if (handleSnackbarOpen) {
            //      handleSnackbarOpen("Stage details loaded!", "info");
            // }
        } catch (err) {
            console.error("Error fetching stage details:", err);
            const errorMessage = err.message || 'Failed to fetch stage details';
            setError(errorMessage);
            setStageDetails(null); // Clear details on error
             if (handleSnackbarOpen) {
                handleSnackbarOpen(`Error fetching stage details: ${errorMessage}`, "error");
            }
        } finally {
            setIsLoading(false);
        }
    }, [stageId, handleSnackbarOpen]); // Depend on stageId

    // useEffect to trigger fetch when stageId changes
    useEffect(() => {
        fetchDetails();
    }, [fetchDetails]);

    return {
        stageDetails,    // The stage detail object (or null)
        isLoading,       // Boolean indicating if fetch is in progress
        error,           // Error object/message if fetch failed
        refreshDetails: fetchDetails // Function to manually trigger a refresh
    };
};

export default useStageDetails;