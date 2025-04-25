// API Test Utility
// This file contains functions to test API connectivity and authentication

import { getStoredCredentials } from './fetchUtils';

/**
 * Test API key authentication
 * @param {string} [businessId] - The business ID (optional, will use stored credentials if not provided)
 * @param {string} [apiKey] - The API key (optional, will use stored credentials if not provided)
 * @returns {Promise<Object>} - The test result
 */
export const testApiKeyAuth = async (businessId, apiKey) => {
  console.log('Testing API key authentication...');
  
  try {
    // If businessId or apiKey is not provided, try to get them from stored credentials
    if (!businessId || !apiKey) {
      const storedCredentials = getStoredCredentials();
      businessId = businessId || storedCredentials.businessId;
      apiKey = apiKey || storedCredentials.businessApiKey;
      
      if (!businessId || !apiKey) {
        return {
          success: false,
          error: 'Business ID and API Key are required'
        };
      }
    }
    
    // Test with different authentication methods
    const authMethods = [
      // Method 1: API key as query parameter
      {
        url: `/businesses/validate-credentials?business_id=${businessId}&api_key=${apiKey}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      },
      // Method 2: API key in X-API-Key header
      {
        url: `/businesses/validate-credentials?business_id=${businessId}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-API-Key': apiKey
        }
      },
      // Method 3: API key in Authorization header as Bearer token
      {
        url: `/businesses/validate-credentials?business_id=${businessId}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      }
    ];
    
    const results = [];
    
    for (const method of authMethods) {
      try {
        console.log(`Testing with URL: ${method.url} and headers:`, method.headers);
        
        const response = await fetch(method.url, {
          method: 'GET',
          headers: method.headers,
          credentials: 'include'
        });
        
        const status = response.status;
        const data = await response.json().catch(() => ({}));
        
        results.push({
          method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
          status,
          data,
          success: response.ok
        });
        
        // If any method succeeds, we can stop testing
        if (response.ok) {
          break;
        }
      } catch (err) {
        console.error(`Error testing authentication method:`, err);
        results.push({
          method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
          error: err.message,
          success: false
        });
      }
    }
    
    // Check if any method succeeded
    const successfulResult = results.find(r => r.success);
    
    return {
      success: !!successfulResult,
      results,
      message: successfulResult ? 'Authentication successful' : 'All authentication methods failed'
    };
  } catch (err) {
    console.error('Error in testApiKeyAuth:', err);
    return {
      success: false,
      error: err.message
    };
  }
};

/**
 * Test template operations
 * @param {string} [businessId] - The business ID (optional, will use stored credentials if not provided)
 * @param {string} [apiKey] - The API key (optional, will use stored credentials if not provided)
 * @returns {Promise<Object>} - The test result
 */
export const testTemplateOperations = async (businessId, apiKey) => {
  console.log('Testing template operations...');
  
  try {
    // If businessId or apiKey is not provided, try to get them from stored credentials
    if (!businessId || !apiKey) {
      const storedCredentials = getStoredCredentials();
      businessId = businessId || storedCredentials.businessId;
      apiKey = apiKey || storedCredentials.businessApiKey;
      
      if (!businessId || !apiKey) {
        return {
          success: false,
          error: 'Business ID and API Key are required'
        };
      }
    }
    
    // Test fetching templates
    const fetchResult = await testFetchTemplates(businessId, apiKey);
    
    // Test creating a template
    const createResult = await testCreateTemplate(businessId, apiKey);
    
    return {
      success: fetchResult.success && createResult.success,
      fetchResult,
      createResult
    };
  } catch (err) {
    console.error('Template operations test error:', err);
    return {
      success: false,
      error: err.message
    };
  }
};

/**
 * Test fetching templates
 * @param {string} businessId - The business ID
 * @param {string} apiKey - The API key
 * @returns {Promise<Object>} - The test result
 */
const testFetchTemplates = async (businessId, apiKey) => {
  console.log('Testing fetching templates...');
  
  try {
    // Try both methods: GET with params and POST with body
    const methods = [
      // Method 1: GET request with business_id as query parameter
      {
        method: 'GET',
        url: `/templates?business_id=${businessId}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
          'X-API-Key': apiKey
        },
        body: null
      },
      // Method 2: POST request with business_id in body
      {
        method: 'POST',
        url: '/templates',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
          'X-API-Key': apiKey
        },
        body: JSON.stringify({ business_id: businessId })
      }
    ];
    
    // Try each method until one succeeds
    for (const method of methods) {
      try {
        console.log(`Trying to fetch templates with ${method.method} request:`, method);
        
        const response = await fetch(method.url, {
          method: method.method,
          headers: method.headers,
          body: method.body,
          credentials: 'include'
        });
        
        const status = response.status;
        const data = await response.json().catch(() => ({}));
        
        console.log(`${method.method} templates result:`, { status, data });
        
        if (response.ok) {
          return {
            success: true,
            status,
            data,
            method: method.method
          };
        }
      } catch (err) {
        console.error(`Error with ${method.method} templates request:`, err);
      }
    }
    
    return {
      success: false,
      error: "All template fetch methods failed"
    };
  } catch (err) {
    console.error('Fetch templates error:', err);
    return {
      success: false,
      error: err.message
    };
  }
};

/**
 * Test creating a template
 * @param {string} businessId - The business ID
 * @param {string} apiKey - The API key
 * @returns {Promise<Object>} - The test result
 */
const testCreateTemplate = async (businessId, apiKey) => {
  console.log('Testing creating a template...');
  
  try {
    const templateData = {
      template_name: `Test Template ${Date.now()}`,
      template_text: 'This is a test template with {variable1} and {variable2}.',
      template_type: 'test_template',
      business_id: businessId,
      variables: ['variable1', 'variable2'],
      template_description: 'A test template for API testing'
    };
    
    const response = await fetch('/templates/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      credentials: 'include',
      body: JSON.stringify(templateData)
    });
    
    const status = response.status;
    const data = await response.json().catch(() => ({}));
    
    console.log('Create template result:', { status, data });
    
    return {
      success: response.ok,
      status,
      data
    };
  } catch (err) {
    console.error('Create template error:', err);
    return {
      success: false,
      error: err.message
    };
  }
};

/**
 * Run all API tests
 * @param {string} [businessId] - The business ID (optional, will use stored credentials if not provided)
 * @param {string} [apiKey] - The API key (optional, will use stored credentials if not provided)
 * @returns {Promise<Object>} - The test results
 */
export const runAllApiTests = async (businessId, apiKey) => {
  console.log('Running all API tests...');
  
  try {
    // If businessId or apiKey is not provided, try to get them from stored credentials
    if (!businessId || !apiKey) {
      const storedCredentials = getStoredCredentials();
      businessId = businessId || storedCredentials.businessId;
      apiKey = apiKey || storedCredentials.businessApiKey;
      
      if (!businessId || !apiKey) {
        return {
          success: false,
          error: 'Business ID and API Key are required'
        };
      }
    }
    
    const authResult = await testApiKeyAuth(businessId, apiKey);
    const templateResult = await testTemplateOperations(businessId, apiKey);
    
    return {
      success: authResult.success && templateResult.success,
      authResult,
      templateResult
    };
  } catch (err) {
    console.error('API tests error:', err);
    return {
      success: false,
      error: err.message
    };
  }
};