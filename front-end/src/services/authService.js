// Authentication service for handling login, logout, and session management
import { API_CONFIG, AUTH_CONFIG } from '../config';

/**
 * Handles API responses and throws errors for non-OK responses
 * @param {Response} response - The fetch Response object
 * @returns {Promise<any>} - The parsed response data
 * @throws {Error} - Throws an error with details from the response if not ok
 */
const handleApiResponse = async (response) => {
  console.log('API Response Status:', response.status, response.statusText);
  console.log('Response Headers:', Object.fromEntries(response.headers.entries()));
  
  // Clone the response so we can try both JSON and text parsing if needed
  const responseClone = response.clone();
  
  // Handle non-OK responses
  if (!response.ok) {
    // Try to get detailed error from response
    try {
      const errorData = await response.json();
      console.error('Error response data:', errorData);
      throw new Error(errorData.message || errorData.error || `API error: ${response.status}`);
    } catch (jsonError) {
      // If response isn't valid JSON, use status text
      console.error('Error parsing response:', jsonError);
      try {
        const errorText = await responseClone.text();
        console.error('Response text:', errorText);
        throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
      } catch (textError) {
        // If both JSON and text parsing fail, just use the status
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
    }
  }
  
  // For successful responses, parse JSON or return empty object
  try {
    const data = await response.json();
    console.log('API Response Data:', data);
    return data;
  } catch (error) {
    // Some successful responses may not have a body (e.g., 204 No Content)
    console.log('No JSON in successful response');
    return {};
  }
};

/**
 * Login with business and user credentials
 * @param {string} userId - User ID
 * @param {string} businessId - Business ID
 * @param {string} businessApiKey - Business API Key
 * @returns {Promise<Object>} - Login response data
 */
export const login = async (userId, businessId, businessApiKey) => {
  try {
    // Trim whitespace from all inputs
    const trimmedUserId = userId.trim();
    const trimmedBusinessId = businessId.trim();
    const trimmedBusinessApiKey = businessApiKey.trim();
    
    console.log('Login attempt with:', { 
      userId: trimmedUserId, 
      businessId: trimmedBusinessId, 
      businessApiKey: '***' 
    });
    console.log('Login URL:', `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`);
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        userId: trimmedUserId,
        businessId: trimmedBusinessId,
        businessApiKey: trimmedBusinessApiKey
      })
    });

    const data = await handleApiResponse(response);
    
    // Check if the response indicates success
    if (data.success || data.message === 'Configuration saved successfully') {
      console.log('Login successful, storing credentials');
      // Store credentials in localStorage for persistent login
      localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.USER_ID, trimmedUserId);
      localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_ID, trimmedBusinessId);
      localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_API_KEY, trimmedBusinessApiKey);
      
      // Return a standardized success response
      return { success: true, message: 'Login successful' };
    } else {
      console.error('Login response indicates failure:', data);
      return { success: false, message: data.error || 'Login failed' };
    }
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, message: error.message || 'Login failed' };
  }
};

/**
 * Logout and clear stored credentials
 */
export const logout = () => {
  // Clear stored credentials
  localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.USER_ID);
  localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_ID);
  localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_API_KEY);
  
  return { success: true, message: 'Logged out successfully' };
};

/**
 * Check if user is logged in
 * @returns {boolean} - True if user is logged in
 */
export const isLoggedIn = () => {
  const userId = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.USER_ID);
  const businessId = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_ID);
  const businessApiKey = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_API_KEY);
  
  return !!(userId && businessId && businessApiKey);
};

/**
 * Get stored credentials
 * @returns {Object} - Stored credentials
 */
export const getStoredCredentials = () => {
  return {
    userId: localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.USER_ID) || '',
    businessId: localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_ID) || '',
    businessApiKey: localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_API_KEY) || ''
  };
};

/**
 * Get authentication headers for API requests
 * @returns {Object} - Headers object with authentication
 */
export const getAuthHeaders = () => {
  const businessApiKey = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.BUSINESS_API_KEY);
  
  if (!businessApiKey) {
    throw new Error('No API key found. Please log in first.');
  }
  
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'businessapikey': businessApiKey,
    'Authorization': `Bearer ${businessApiKey}`
  };
};

// Create a named export object
const authService = {
  login,
  logout,
  isLoggedIn,
  getStoredCredentials,
  getAuthHeaders
};

export default authService;