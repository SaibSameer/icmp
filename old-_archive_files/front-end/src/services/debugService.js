// Debug service for message handling diagnostics
import { API_CONFIG } from '../config';
import { getAuthHeaders } from './authService';

/**
 * Handles API responses and throws errors for non-OK responses
 * @param {Response} response - The fetch Response object
 * @returns {Promise<any>} - The parsed response data
 * @throws {Error} - Throws an error with details from the response if not ok
 */
const handleApiResponse = async (response) => {
    // Handle non-OK responses
    if (!response.ok) {
        // Try to get detailed error from response
        try {
            const errorData = await response.json();
            throw new Error(errorData.message || errorData.error || `API error: ${response.status}`);
        } catch (jsonError) {
            // If response isn't valid JSON, use status text
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
    }
    
    // For successful responses, parse JSON or return empty object
    try {
        return await response.json();
    } catch (error) {
        // Some successful responses may not have a body (e.g., 204 No Content)
        return {};
    }
};

/**
 * Make an API request with authentication
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Request options
 * @returns {Promise<any>} - Response data
 */
const apiRequest = async (endpoint, options = {}) => {
    const url = `${endpoint}`;
    const defaultOptions = {
        headers: getAuthHeaders(),
        credentials: 'include',
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    return handleApiResponse(response);
};

export const debugService = {
    // Get debug information for a specific conversation
    getConversationDebug: (conversationId) => {
        return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/conversation/${conversationId}`);
    },

    // Get real-time message processing debug info
    getMessageProcessingDebug: (messageId) => {
        return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/message/${messageId}`);
    },

    // Get stage navigation history
    getStageNavigationDebug: (conversationId) => {
        return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/stages/${conversationId}`);
    },

    // Get prompt generation details
    getPromptGenerationDebug: (messageId) => {
        return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/prompts/${messageId}`);
    },

    // Get data extraction results
    getDataExtractionDebug: (messageId) => {
        return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/extraction/${messageId}`);
    },

    // Subscribe to real-time debug events for a conversation
    subscribeToDebugEvents: (conversationId, callback) => {
        const eventSource = new EventSource(`${API_CONFIG.ENDPOINTS.DEBUG}/events/${conversationId}`);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                callback(data);
            } catch (error) {
                console.error('Error parsing event data:', error);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventSource.close();
        };

        // Return cleanup function
        return () => {
            if (eventSource.readyState !== EventSource.CLOSED) {
                eventSource.close();
            }
        };
    }
};

export default debugService;