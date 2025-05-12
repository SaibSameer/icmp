// Message service for handling message sending and conversation history
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
 * Send a message to the API
 * @param {string} message - Message content
 * @param {string} businessId - Business ID
 * @param {string} userId - User ID
 * @param {Object} options - Additional options
 * @param {string} options.conversationId - Optional conversation ID
 * @param {string} options.agentId - Optional agent ID
 * @returns {Promise<Object>} - Response data
 */
export const sendMessage = async (message, businessId, userId, options = {}) => {
  try {
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
    
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(requestData)
    });
    
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Send message error:', error);
    throw error;
  }
};

/**
 * Fetch conversation history for a business
 * @param {string} businessId - Business ID
 * @returns {Promise<Array>} - Conversation history
 */
export const fetchConversationHistory = async (businessId) => {
  try {
    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/conversations?business_id=${businessId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/health`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Test connection error:', error);
    throw error;
  }
};

/**
 * Fetch user message counts for a business
 * @param {string} businessId - Business ID
 * @returns {Promise<Array>} - Array of { user_id, message_count }
 */
export const fetchUserMessageCounts = async (businessId) => {
  try {
    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/user-stats/message-counts?business_id=${businessId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      }
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch user message counts error:', error);
    throw error;
  }
};

/**
 * Fetch messages for a specific user
 * @param {string} businessId - Business ID
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of message objects
 */
export const fetchUserMessages = async (businessId, userId) => {
  try {
    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/messages/user/${userId}?business_id=${businessId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      }
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch user messages error:', error);
    throw error;
  }
};

export default {
  sendMessage,
  fetchConversationHistory,
  testConnection,
  fetchUserMessageCounts,
  fetchUserMessages
};