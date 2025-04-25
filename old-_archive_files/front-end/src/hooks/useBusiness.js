// src/hooks/useBusiness.js
import { useState, useEffect } from 'react';
import axios from 'axios';

const useBusiness = (handleSnackbarOpen) => {
    const [businessDetails, setBusinessDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchBusinessDetails = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get('/api/business');
                setBusinessDetails(response.data);
                setError(null);
            } catch (err) {
                setError(err.message);
                if (handleSnackbarOpen) {
                    handleSnackbarOpen('Failed to load business details', 'error');
                }
            } finally {
                setIsLoading(false);
            }
        };

        fetchBusinessDetails();
    }, [handleSnackbarOpen]);

    return { businessDetails, isLoading, error };
};

export default useBusiness;