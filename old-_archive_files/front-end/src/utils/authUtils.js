/**
 * Authentication utility functions
 */

/**
 * Get stored credentials from localStorage
 * @returns {Object} Object containing businessId and businessApiKey
 */
export const getStoredCredentials = () => {
  const businessId = localStorage.getItem('businessId');
  const businessApiKey = localStorage.getItem('businessApiKey');
  
  return {
    businessId,
    businessApiKey
  };
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user is authenticated, false otherwise
 */
export const isAuthenticated = () => {
  const { businessId, businessApiKey } = getStoredCredentials();
  return !!(businessId && businessApiKey);
};

/**
 * Store credentials in localStorage
 * @param {string} businessId - The business ID
 * @param {string} businessApiKey - The business API key
 */
export const storeCredentials = (businessId, businessApiKey) => {
  localStorage.setItem('businessId', businessId);
  localStorage.setItem('businessApiKey', businessApiKey);
};

/**
 * Clear stored credentials from localStorage
 */
export const clearCredentials = () => {
  localStorage.removeItem('businessId');
  localStorage.removeItem('businessApiKey');
};