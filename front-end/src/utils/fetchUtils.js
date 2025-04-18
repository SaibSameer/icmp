// Global request cache to prevent duplicate API calls
const apiCache = {
  cache: {},
  get: function(url) {
    return this.cache[url]?.data;
  },
  set: function(url, data, ttl = 60000) { // Default TTL: 1 minute
    this.cache[url] = {
      data,
      expiry: Date.now() + ttl
    };
  },
  isValid: function(url) {
    const item = this.cache[url];
    return item && item.expiry > Date.now();
  },
  clear: function() {
    this.cache = {};
  }
};

/**
 * Get stored credentials from localStorage
 * @returns {Object} Object containing businessId and businessApiKey
 */
export const getStoredCredentials = () => {
  const businessId = localStorage.getItem('businessId');
  const businessApiKey = localStorage.getItem('businessApiKey');
  return { businessId, businessApiKey };
};

/**
 * Fetches data with caching support
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} - The fetch response
 */
export const cachedFetch = async (url, options = {}) => {
  // Ensure URL ends with trailing slash for POST/PUT requests
  if ((options.method === 'POST' || options.method === 'PUT') && !url.endsWith('/')) {
    url = `${url}/`;
  }
  
  // Add business_id to URL if not already present
  const urlObj = new URL(url, window.location.origin);
  if (!urlObj.searchParams.has('business_id')) {
    const businessId = localStorage.getItem('businessId');
    if (businessId) {
      urlObj.searchParams.append('business_id', businessId);
      url = urlObj.toString();
    }
  }
  
  // Create cache key
  const cacheKey = `${url}-${options.method || 'GET'}-${JSON.stringify(options.body || {})}`;
  
  // Check cache for GET requests
  if (options.method === 'GET' || !options.method) {
    const cachedData = apiCache.get(cacheKey);
    if (cachedData && apiCache.isValid(cacheKey)) {
      console.log(`Using cached data for ${url}`);
      return new Response(JSON.stringify(cachedData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
  
  // Prepare headers
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...options.headers
  };
  
  // Add API key in both headers for redundancy
  const apiKey = localStorage.getItem('businessApiKey');
  if (apiKey) {
    // Use both X-API-Key and Authorization header to maximize compatibility
    headers['X-API-Key'] = apiKey;
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  // Prepare fetch options
  const fetchOptions = {
    ...options,
    headers,
    credentials: 'include' // Important: Send cookies with request
  };
  
  // Stringify body if it's an object
  if (fetchOptions.body && typeof fetchOptions.body === 'object') {
    fetchOptions.body = JSON.stringify(fetchOptions.body);
  }
  
  // Make the fetch request
  console.log(`Fetching ${url} with options:`, fetchOptions);
  const response = await fetch(url, fetchOptions);
  
  // Cache successful GET responses
  if ((options.method === 'GET' || !options.method) && response.ok) {
    const data = await response.clone().json().catch(() => null);
    if (data) {
      apiCache.set(cacheKey, data);
    }
  }
  
  return response;
};