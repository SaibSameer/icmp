const API_BASE_URL = '';

async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        },
        credentials: 'include',
        ...options
    };

    const response = await fetch(url, defaultOptions);

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

// LLM-related API calls
const llmService = {
    /**
     * Fetch recent LLM calls for the current business
     * @param {string} internalApiKey - Internal API key for authorization
     * @param {number} limit - Maximum number of calls to fetch (default: 10)
     * @returns {Promise<Array>} Array of LLM call objects
     */
    getRecentCalls: async (internalApiKey, limit = 10) => {
        try {
            const response = await request(`/api/llm/calls/recent?limit=${limit}`, {
                headers: {
                    Authorization: `Bearer ${internalApiKey}`
                }
            });
            
            // Ensure each call has a timestamp field
            return response.map(call => ({
                ...call,
                timestamp: call.timestamp || call.created_at
            }));
        } catch (error) {
            console.error('Error fetching recent calls:', error);
            throw error;
        }
    },

    /**
     * Fetch details of a specific LLM call
     * @param {string} internalApiKey - Internal API key for authorization
     * @param {string} callId - ID of the LLM call to fetch
     * @returns {Promise<Object>} LLM call details
     */
    getCallDetails: async (internalApiKey, callId) => {
        try {
            const response = await request(`/api/llm/calls/${callId}`, {
                headers: {
                    Authorization: `Bearer ${internalApiKey}`
                }
            });
            
            // Ensure the call has a timestamp field
            return {
                ...response,
                timestamp: response.timestamp || response.created_at
            };
        } catch (error) {
            console.error('Error fetching call details:', error);
            throw error;
        }
    },

    /**
     * Send a message to the LLM and get a response
     * @param {string} internalApiKey - Internal API key for authorization
     * @param {string} message - The message to send
     * @param {Object} options - Additional options for the message
     * @returns {Promise<Object>} LLM response
     */
    sendMessage: async (internalApiKey, message, options = {}) => {
        return request('/api/llm/messages', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${internalApiKey}`
            },
            body: JSON.stringify({
                message,
                ...options
            })
        });
    },

    /**
     * Get conversation history
     * @param {string} internalApiKey - Internal API key for authorization
     * @param {string} conversationId - ID of the conversation
     * @returns {Promise<Array>} Array of messages in the conversation
     */
    getConversationHistory: async (internalApiKey, conversationId) => {
        return request(`/api/llm/conversations/${conversationId}`, {
            headers: {
                Authorization: `Bearer ${internalApiKey}`
            }
        });
    },

    /**
     * Start a new conversation
     * @param {string} internalApiKey - Internal API key for authorization
     * @returns {Promise<Object>} New conversation details
     */
    startConversation: async (internalApiKey) => {
        return request('/api/llm/conversations', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${internalApiKey}`
            }
        });
    },

    /**
     * End a conversation
     * @param {string} internalApiKey - Internal API key for authorization
     * @param {string} conversationId - ID of the conversation to end
     * @returns {Promise<Object>} Conversation end status
     */
    endConversation: async (internalApiKey, conversationId) => {
        return request(`/api/llm/conversations/${conversationId}/end`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${internalApiKey}`
            }
        });
    }
};

export default llmService; 