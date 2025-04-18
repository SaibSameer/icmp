// File: src/components/healthCheckService.js
const API_ENDPOINT = '/health';

export const getHealthCheck = async () => {
    try {
        const apiKey = process.env.REACT_APP_API_KEY; // Access the API key from environment variables

        if (!apiKey) {
            throw new Error("ICMP API Key is missing. Ensure REACT_APP_API_KEY is set in your environment.");
        }

        const response = await fetch(API_ENDPOINT, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            const errorMessage = errorData.message || `HTTP error! Status: ${response.status}`;
            throw new Error(errorMessage);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching health check:", error);
        throw error;
    }
};