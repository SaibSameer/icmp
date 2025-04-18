// src/services/stageService.js

import { API_CONFIG } from '../config';
import { getAuthHeaders } from '../services/authService';

// Helper to handle API responses (reuse or import)
const handleApiResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); 
    throw new Error(errorData.message || errorData.error || `HTTP error ${response.status}`);
  }
  if (response.status === 204) {
      return null; 
  }
  // Assume the response is JSON if OK and not 204
  return response.json(); 
};

// Fetch all stages for a given business
export const fetchStages = async (businessId) => {
  if (!businessId) {
    console.error("[Service Error] fetchStages requires a businessId.");
    throw new Error("Business ID is required to fetch stages.");
  }
  console.log(`[Service] Fetching stages for business: ${businessId}`);
  
  // Log the headers for debugging
  const headers = getAuthHeaders();
  console.log("[Service] Using headers:", headers);
  
  const response = await fetch(`/stages?business_id=${businessId}`, {
    method: 'GET',
    credentials: 'include', // Send cookies
    headers: headers
  });
  
  // Log the response status for debugging
  console.log(`[Service] Response status: ${response.status}`);
  
  return handleApiResponse(response);
};

// Create a new stage
export const createStage = async (stageData) => {
  if (!stageData.business_id) {
    console.error("[Service Error] createStage requires a business_id.");
    throw new Error("Business ID is required to create a stage.");
  }
  
  console.log(`[Service] Creating stage for business: ${stageData.business_id}`);
  console.log(`[Service] Stage data:`, stageData);
  
  // Log the headers for debugging
  const headers = getAuthHeaders();
  console.log("[Service] Using headers:", headers);
  
  const response = await fetch(`/stages`, {
    method: 'POST',
    credentials: 'include',
    headers: headers,
    body: JSON.stringify(stageData)
  });
  
  // Log the response status for debugging
  console.log(`[Service] Response status: ${response.status}`);
  
  return handleApiResponse(response);
};

// Fetch details for a specific stage
export const fetchStageDetails = async (stageId) => {
    try {
        const businessId = localStorage.getItem('businessId');
        if (!businessId || !stageId) {
            throw new Error('Missing required parameters: ' + 
                (!businessId ? 'businessId ' : '') + 
                (!stageId ? 'stageId' : ''));
        }

        console.log(`[Service] Fetching stage details for stage ${stageId} and business ${businessId}`);
        
        // Log the headers for debugging
        const headers = getAuthHeaders();
        console.log("[Service] Using headers:", headers);
        
        const response = await fetch(`/stages/${stageId}?business_id=${businessId}`, {
            method: 'GET',
            credentials: 'include',
            headers: headers
        });

        // Log the response status for debugging
        console.log(`[Service] Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error response:', errorData);
            throw new Error(errorData.error || `Failed to fetch stage details (HTTP ${response.status})`);
        }

        const data = await response.json();
        console.log('Received stage details:', data);
        
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid response format from server');
        }

        return data;
    } catch (error) {
        console.error('Error fetching stage details:', error);
        throw error;
    }
};

// Update an existing stage
export const updateStage = async (stageId, stageData) => {
    if (!stageId || !stageData.business_id) {
        throw new Error('Missing required parameters: stageId and business_id');
    }
    
    console.log(`[Service] Updating stage ${stageId} for business ${stageData.business_id}`);
    
    // Log the headers for debugging
    const headers = getAuthHeaders();
    console.log("[Service] Using headers:", headers);
    
    const response = await fetch(`/stages/${stageId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: headers,
        body: JSON.stringify(stageData)
    });
    
    // Log the response status for debugging
    console.log(`[Service] Response status: ${response.status}`);
    
    return handleApiResponse(response);
};

// Delete a stage
export const deleteStage = async (stageId, businessId) => {
    if (!stageId || !businessId) {
        throw new Error('Missing required parameters: stageId and businessId');
    }
    
    console.log(`[Service] Deleting stage ${stageId} for business ${businessId}`);
    
    // Log the headers for debugging
    const headers = getAuthHeaders();
    console.log("[Service] Using headers:", headers);
    
    const response = await fetch(`/stages/${stageId}?business_id=${businessId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: headers
    });
    
    // Log the response status for debugging
    console.log(`[Service] Response status: ${response.status}`);
    
    return handleApiResponse(response);
};