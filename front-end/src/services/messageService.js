// Message service for handling message sending and conversation history
import { API_CONFIG } from '../config';
import { getAuthHeaders, getStoredCredentials } from './authService';

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
 * Send a message to the API
 * @param {string} message - Message content
 * @param {Object} options - Additional options
 * @param {string} options.conversationId - Optional conversation ID
 * @param {string} options.agentId - Optional agent ID
 * @returns {Promise<Object>} - Response data
 */
export const sendMessage = async (message, options = {}) => {
  try {
    const { userId, businessId } = getStoredCredentials();
    
    const requestData = {
      business_id: businessId,
      user_id: userId,
      message: message
    };
    
    // Add optional fields if provided
    if (options.conversationId) {
      requestData.conversation_id = options.conversationId;
    }
    
    if (options.agentId) {
      requestData.agent_id = options.agentId;
    }
    
    const response = await fetch(`${API_CONFIG.ENDPOINTS.MESSAGE}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'include',
      body: JSON.stringify(requestData)
    });
    
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Send message error:', error);
    throw error;
  }
};

/**
 * Fetch conversation history for a user
 * @returns {Promise<Array>} - Conversation history
 */
export const fetchConversationHistory = async () => {
  try {
    const { userId, businessId } = getStoredCredentials();
    
    const response = await fetch(
      `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CONVERSATIONS}/?business_id=${businessId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      }
    );
    
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Fetch conversation history error:', error);
    throw error;
  }
};

/**
 * Test backend connection
 * @returns {Promise<Object>} - Connection test result
 */
export const testConnection = async () => {
  try {
    const response = await fetch(`/`, {
      method: 'GET',
      credentials: 'include'
    });
    
    const text = await response.text();
    return { success: true, message: text };
  } catch (error) {
    console.error('Connection test error:', error);
    return { success: false, message: error.message };
  }
};

export default {
  sendMessage,
  fetchConversationHistory,
  testConnection
};