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
 * @param {string} options.senderType - Optional sender type ('user', 'staff', 'assistant', or 'ai')
 * @returns {Promise<Object>} - Response data
 */
export const sendMessage = async (message, businessId, userId, options = {}) => {
  try {
    const requestData = {
      business_id: businessId,
      user_id: userId,
      message: message,
      sender_type: options.senderType || 'user' // Default to 'user' if not specified
    };
    
    // Add optional fields if provided
    if (options.conversationId) {
      requestData.conversation_id = options.conversationId;
    }
    
    if (options.agentId) {
      requestData.agent_id = options.agentId;
    }
    
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/message`, {
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
 * @returns {Promise<Array>} - Array of conversations
 */
export const fetchConversationHistory = async (businessId) => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/conversations?business_id=${businessId}`, {
      headers: getAuthHeaders()
    });
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Fetch conversation history error:', error);
    throw error;
  }
};

/**
 * Test the connection to the API
 * @returns {Promise<Object>} - Response data
 */
export const testConnection = async () => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/health`, {
      headers: getAuthHeaders()
    });
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Test connection error:', error);
    throw error;
  }
};

/**
 * Stop or resume AI responses for a conversation or user
 * @param {string} conversationId - Conversation ID
 * @param {string} userId - Optional user ID
 * @param {string} action - 'stop', 'resume', or 'status'
 * @param {number} duration - Optional duration in hours
 * @returns {Promise<Object>} - Response data
 */
export const stopAIResponses = async (conversationId, userId = null, action = 'stop', duration = null) => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/conversations/${conversationId}/ai-control`, {
      method: action === 'status' ? 'GET' : 'POST',
      headers: getAuthHeaders(),
      body: action !== 'status' ? JSON.stringify({
        action,
        user_id: userId,
        duration
      }) : undefined
    });
    return await handleApiResponse(response);
  } catch (error) {
    console.error('Stop AI responses error:', error);
    throw error;
  }
};

export default {
  sendMessage,
  fetchConversationHistory,
  testConnection,
  stopAIResponses
};