/**
 * Get authentication headers for API requests
 * @returns {Object} Headers object with Authorization and Content-Type
 */
export const getAuthHeaders = () => {
    const adminApiKey = sessionStorage.getItem('adminApiKey');
    return {
        'Authorization': `Bearer ${adminApiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has an API key
 */
export const isAuthenticated = () => {
    const adminApiKey = sessionStorage.getItem('adminApiKey');
    return !!adminApiKey;
};

/**
 * Store authentication token
 * @param {string} token - The API key to store
 */
export const setAuthToken = (token) => {
    sessionStorage.setItem('adminApiKey', token);
};

/**
 * Remove authentication token
 */
export const removeAuthToken = () => {
    sessionStorage.removeItem('adminApiKey');
};