// Configuration settings for the application

// API Configuration
const API_CONFIG = {
  // Base URL for API requests
  BASE_URL: process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
  
  // API endpoints
  ENDPOINTS: {
    LOGIN: '/api/save-config',
    MESSAGE: '/api/message',
    CONVERSATIONS: '/api/conversations',
    BUSINESSES: '/businesses',
    STAGES: '/api/stages',
    TEMPLATES: '/templates',
    AGENTS: '/agents',
    DEBUG: '/debug'
  },
  
  // Default values
  DEFAULTS: {
    BUSINESS_ID: '1c8cde77-0306-42dd-a0b6-c366a07651ad',
    API_KEY: 'default_api_key',
    USER_ID: '00000000-0000-0000-0000-000000000000'
  }
};

// Enhanced debugging for environment variables
console.log('Environment Variables Debug:');
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
console.log('REACT_APP_API_BASE_URL:', process.env.REACT_APP_API_BASE_URL);
console.log('All environment variables:', process.env);
console.log('API Configuration:', {
  baseUrl: API_CONFIG.BASE_URL,
  endpoints: API_CONFIG.ENDPOINTS
});

// Authentication settings
const AUTH_CONFIG = {
  // Cookie names
  COOKIES: {
    BUSINESS_API_KEY: 'businessApiKey'
  },
  
  // Local storage keys
  STORAGE_KEYS: {
    USER_ID: 'userId',
    BUSINESS_ID: 'businessId',
    BUSINESS_API_KEY: 'businessApiKey'
  }
};

// UI Configuration
const UI_CONFIG = {
  // Snackbar settings
  SNACKBAR: {
    AUTO_HIDE_DURATION: 6000,
    POSITION: { vertical: 'top', horizontal: 'center' }
  },
  
  // Debug panel settings
  DEBUG_PANEL: {
    ID: 'debugPanel'
  }
};

export { API_CONFIG, AUTH_CONFIG, UI_CONFIG };