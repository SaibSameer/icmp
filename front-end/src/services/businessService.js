import { API_CONFIG } from '../config';
import { getAuthHeaders } from '../services/authService';

// Helper to handle API responses (can be moved to a shared api.js)
const handleApiResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); // Try to parse error, fallback
    throw new Error(errorData.message || errorData.error || `HTTP error ${response.status}`);
  }
  // Handle 204 No Content
  if (response.status === 204) {
      return null; 
  }
  return response.json();
};

// Fetch business details by ID
export const getBusiness = async (businessId) => {
  console.log(`[Service] Fetching business details for ID: ${businessId}`);
  const response = await fetch(`${API_CONFIG.BASE_URL}/businesses/${businessId}`, {
    method: 'GET',
    credentials: 'include', // Send cookies
    headers: getAuthHeaders()
  });
  return handleApiResponse(response);
};

// Update business details
export const updateBusiness = async (businessId, businessData) => {
  console.log(`[Service] Updating business ${businessId} with:`, businessData);
  const response = await fetch(`${API_CONFIG.BASE_URL}/businesses/${businessId}`, {
    method: 'PUT',
    credentials: 'include',
    headers: getAuthHeaders(),
    body: JSON.stringify(businessData),
  });
  return handleApiResponse(response);
};

// Set the default starting stage for a business
export const setDefaultStage = async (businessId, stageId) => {
  console.log(`[Service] Setting default stage for business ${businessId} to: ${stageId}`);
  const response = await fetch(`${API_CONFIG.BASE_URL}/businesses/${businessId}/default-stage`, {
    method: 'PUT',
    credentials: 'include',
    headers: getAuthHeaders(),
    body: JSON.stringify({ stage_id: stageId }), // Send stage_id in the body
  });
  return handleApiResponse(response);
};