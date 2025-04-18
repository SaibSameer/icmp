import { API_CONFIG } from '../config';
import { getAuthHeaders, getStoredCredentials } from './authService';

/**
 * Standardized handler for API responses
 * @param {Response} response - The fetch Response object
 * @returns {Promise<any>} - The parsed response data
 * @throws {Error} - Throws an error with details from the response if not ok
 */
export const handleApiResponse = async (response) => {
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
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: getAuthHeaders(),
    credentials: 'include',
  };

  const response = await fetch(url, { ...defaultOptions, ...options });
  return handleApiResponse(response);
};

export const apiService = {
  // Businesses
  getBusinessDetails: async (businessId) => {
    return apiRequest(`${API_CONFIG.ENDPOINTS.BUSINESSES}/${businessId}`);
  },
  
  // Stages
  getStages: async (businessId) => {
    return apiRequest(`${API_CONFIG.ENDPOINTS.STAGES}?business_id=${businessId}`);
  },
  
  createStage: async (stageData) => {
    return apiRequest(API_CONFIG.ENDPOINTS.STAGES, {
      method: 'POST',
      body: JSON.stringify(stageData),
    });
  },
  
  // Authentication
  saveConfig: async (config) => {
    return apiRequest(API_CONFIG.ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },
  
  // Templates
  createTemplate: async (templateData) => {
    return apiRequest(API_CONFIG.ENDPOINTS.TEMPLATES, {
      method: 'POST',
      body: JSON.stringify(templateData),
    });
  },
  
  fetchTemplateDetails: async (templateId) => {
    return apiRequest(`${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}`);
  },
  
  // Messages
  sendMessage: async (messageData) => {
    return apiRequest(API_CONFIG.ENDPOINTS.MESSAGE, {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  },
  
  // Conversations
  getConversations: async (userId, businessId) => {
    return apiRequest(`${API_CONFIG.ENDPOINTS.CONVERSATIONS}/${userId}?business_id=${businessId}`);
  },
  
  // Debug
  getDebugInfo: async (conversationId) => {
    return apiRequest(`${API_CONFIG.ENDPOINTS.DEBUG}/conversation/${conversationId}`);
  }
};

export default apiService;