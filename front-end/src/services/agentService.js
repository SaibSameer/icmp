// src/services/agentService.js
import { API_CONFIG } from '../config';
import { getAuthHeaders } from '../services/authService';
import { normalizeUUID } from '../hooks/useConfig';

// Fetch agents for a business
export const fetchAgents = async (businessId) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    console.log(`Fetching agents for business: ${normalizedBusinessId}`);
    
    const url = `${API_CONFIG.BASE_URL}/api/agents?business_id=${normalizedBusinessId}`;
    console.log('Fetch URL:', url);
    console.log('Headers:', getAuthHeaders());
    
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    console.log('Response status:', response.status);
    const responseData = await response.json();
    console.log('Response data:', responseData);
    
    if (!response.ok) {
      throw new Error(responseData.message || 'Failed to fetch agents');
    }

    // Ensure we always return an array
    const agents = Array.isArray(responseData) ? responseData : [];
    console.log('Processed agents:', agents);
    return agents;
  } catch (error) {
    console.error('Error in fetchAgents:', error);
    throw error;
  }
};

// Create a new agent
export const createAgent = async (agentData) => {
  try {
    // Make sure business_id is normalized
    const normalizedData = {
      ...agentData,
      business_id: normalizeUUID(agentData.business_id)
    };
    
    console.log('Creating agent with data:', normalizedData);
    const url = `${API_CONFIG.BASE_URL}/api/agents`;
    console.log('Create URL:', url);
    console.log('Headers:', getAuthHeaders());
    
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(normalizedData)
    });
    
    console.log('Create response status:', response.status);
    const responseData = await response.json();
    console.log('Create response data:', responseData);
    
    if (!response.ok) {
      throw new Error(responseData.message || 'Failed to create agent');
    }

    return responseData;
  } catch (error) {
    console.error('Error in createAgent:', error);
    throw error;
  }
};

// Update an existing agent
export const updateAgent = async (agentId, agentData) => {
  try {
    // Make sure business_id is normalized
    const normalizedData = {
      ...agentData,
      business_id: normalizeUUID(agentData.business_id)
    };
    
    console.log(`Updating agent ${agentId}:`, normalizedData);
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/agents/${agentId}`, {
      method: 'PUT',
      credentials: 'include',
      headers: getAuthHeaders(),
      body: JSON.stringify(normalizedData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update agent');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in updateAgent:', error);
    throw error;
  }
};

// Delete an agent
export const deleteAgent = async (agentId, businessId) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    console.log(`Deleting agent ${agentId} for business ${normalizedBusinessId}`);
    const url = `${API_CONFIG.BASE_URL}/api/agents/${agentId}?business_id=${normalizedBusinessId}`;
    console.log('Delete URL:', url);
    console.log('Headers:', getAuthHeaders());
    
    const response = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    console.log('Delete response status:', response.status);
    const responseData = await response.json();
    console.log('Delete response data:', responseData);
    
    if (!response.ok) {
      throw new Error(responseData.message || 'Failed to delete agent');
    }

    return true;
  } catch (error) {
    console.error('Error in deleteAgent:', error);
    throw error;
  }
};

// Get a specific agent
export const getAgent = async (agentId, businessId) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    console.log(`Fetching agent ${agentId} for business ${normalizedBusinessId}`);
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/agents/${agentId}?business_id=${normalizedBusinessId}`, {
      method: 'GET',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch agent');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getAgent:', error);
    throw error;
  }
};