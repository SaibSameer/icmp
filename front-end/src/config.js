// Configuration settings for the application

// API Configuration
const API_CONFIG = {
  // Base URL for API requests
  BASE_URL: process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE_URL || 'https://icmp-events-api.onrender.com',
  
  // API endpoints
  ENDPOINTS: {
    LOGIN: '/api/save-config',
    MESSAGE: '/api/message',
    CONVERSATIONS: '/api/v1/conversations',
    BUSINESSES: '/businesses',
    STAGES: '/api/stages',
    TEMPLATES: '/api/templates',
    AGENTS: '/agents',
    DEBUG: '/debug',
    VARIABLES: '/api/template-variables'
  },
  
  // Default values
  DEFAULTS: {
    BUSINESS_ID: '1c8cde77-0306-42dd-a0b6-c366a07651ad',
    API_KEY: 'default_api_key',
    USER_ID: '00000000-0000-0000-0000-000000000000'
  }
};

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
    BUSINESS_API_KEY: 'businessApiKey',
    ADMIN_API_KEY: 'adminApiKey'
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

// Development settings
const DEV_CONFIG = {
  ENABLE_LOGGING: process.env.NODE_ENV === 'development',
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000'
};

export { API_CONFIG, AUTH_CONFIG, UI_CONFIG, DEV_CONFIG };