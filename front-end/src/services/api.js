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
    credentials: 'include',
  };

  const requestOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  };

  const response = await fetch(url, requestOptions);
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
    const { businessId } = getStoredCredentials();
    if (!businessId) {
      throw new Error("Business ID not found. Please log in.");
    }
    const dataToSend = { ...templateData, business_id: businessId };
    return apiRequest(API_CONFIG.ENDPOINTS.TEMPLATES, {
      method: 'POST',
      body: JSON.stringify(dataToSend),
    });
  },
  
  fetchTemplateDetails: async (templateId) => {
    const { businessId } = getStoredCredentials();
    if (!businessId) {
      throw new Error("Business ID not found. Please log in.");
    }
    const endpoint = `${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}?business_id=${businessId}`;
    return apiRequest(endpoint);
  },
  
  updateTemplate: async (templateId, templateData) => {
    const { businessId } = getStoredCredentials();
    if (!businessId) {
      throw new Error("Business ID not found. Please log in.");
    }
    const dataToSend = { ...templateData, business_id: businessId };
    const endpoint = `${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}`;
    return apiRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(dataToSend),
    });
  },
  
  deleteTemplate: async (templateId) => {
    const { businessId } = getStoredCredentials();
    if (!businessId) {
      throw new Error("Business ID not found. Please log in.");
    }
    const endpoint = `${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}?business_id=${businessId}`;
    return apiRequest(endpoint, {
      method: 'DELETE',
    });
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
  },

  // Add fetchTemplates method
  fetchTemplates: async (businessId, agentId) => {
    if (!businessId) {
      throw new Error("Business ID is required to fetch templates.");
    }
    if (!agentId) {
        throw new Error("Agent ID is required to fetch templates.");
    }
    // Assuming the endpoint requires both business_id and agent_id as query params
    const endpoint = `${API_CONFIG.ENDPOINTS.TEMPLATES}?business_id=${businessId}&agent_id=${agentId}`;
    return apiRequest(endpoint);
  },

  // Add duplicateTemplate method
  duplicateTemplate: async (templateIdToDuplicate) => {
    // 1. Fetch the original template details
    const originalTemplate = await apiService.fetchTemplateDetails(templateIdToDuplicate); // fetchTemplateDetails already includes businessId

    // 2. Prepare data for the new template
    const newTemplateData = {
      ...originalTemplate,
      template_name: `${originalTemplate.template_name} (Copy)`, // Modify name
      // Remove original ID, the backend will assign a new one
      template_id: undefined,
    };
     // business_id will be added by createTemplate

    // 3. Create the new template
    return apiService.createTemplate(newTemplateData);
  },
};

export default apiService;