import { API_CONFIG } from '../config';
import { getAuthHeaders } from './authService';
import { normalizeUUID } from '../hooks/useConfig';

// Fetch templates
export const fetchTemplates = async (businessId, agentId = null) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    let url = `${API_CONFIG.BASE_URL}/templates?business_id=${normalizedBusinessId}`;
    
    if (agentId) {
      const normalizedAgentId = normalizeUUID(agentId);
      url += `&agent_id=${normalizedAgentId}`;
      console.log(`Fetching templates for business: ${normalizedBusinessId}, agent: ${normalizedAgentId}`);
    } else {
      console.log(`Fetching templates for business: ${normalizedBusinessId}`);
    }

    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch templates');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in fetchTemplates:', error);
    throw error;
  }
};

// Get a template by ID
export const getTemplate = async (templateId, businessId) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    
    console.log(`Fetching template ${templateId} for business: ${normalizedBusinessId}`);
    const response = await fetch(`${API_CONFIG.BASE_URL}/templates/${templateId}?business_id=${normalizedBusinessId}`, {
      method: 'GET',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch template');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getTemplate:', error);
    throw error;
  }
};

// Create a new template
export const createTemplate = async (templateData) => {
  try {
    // Make sure business_id and agent_id are normalized
    const normalizedData = {
      ...templateData,
      business_id: normalizeUUID(templateData.business_id),
      agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null
    };
    
    // Log the normalized data for debugging
    console.log('Creating template with data:', {
      original: templateData.business_id,
      normalized: normalizedData.business_id
    });
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeaders(),
      body: JSON.stringify(normalizedData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to create template');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in createTemplate:', error);
    throw error;
  }
};

// Update an existing template
export const updateTemplate = async (templateId, templateData) => {
  try {
    // Make sure business_id and agent_id are normalized
    const normalizedData = {
      ...templateData,
      business_id: normalizeUUID(templateData.business_id),
      agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null
    };
    
    // Log the normalized data for debugging
    console.log(`Updating template ${templateId}:`, {
      original: templateData.business_id,
      normalized: normalizedData.business_id
    });
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}`, {
      method: 'PUT',
      credentials: 'include',
      headers: getAuthHeaders(),
      body: JSON.stringify(normalizedData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update template');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in updateTemplate:', error);
    throw error;
  }
};

// Delete a template
export const deleteTemplate = async (templateId, businessId) => {
  try {
    const normalizedBusinessId = normalizeUUID(businessId);
    
    console.log(`Deleting template ${templateId} for business: ${normalizedBusinessId}`);
    const response = await fetch(`${API_CONFIG.BASE_URL}/templates/${templateId}?business_id=${normalizedBusinessId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to delete template');
    }

    return true;
  } catch (error) {
    console.error('Error in deleteTemplate:', error);
    throw error;
  }
};

// Duplicate a template
export const duplicateTemplate = async (templateData) => {
  try {
    // Make sure business_id and agent_id are normalized
    const normalizedData = {
      ...templateData,
      business_id: normalizeUUID(templateData.business_id),
      agent_id: normalizeUUID(templateData.agent_id),
      template_name: `${templateData.template_name} (Copy)`
    };
    
    console.log('Duplicating template as:', normalizedData);
    return await createTemplate(normalizedData);
  } catch (error) {
    console.error('Error in duplicateTemplate:', error);
    throw error;
  }
};

export const getTemplateVariables = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/template-variables/', {
      method: 'GET',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        'Authorization': 'Bearer cd0fd3314e8f1fe7cef737db4ac21778ccc7d5a97bbb33d9af17612e337231d6',
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch template variables');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getTemplateVariables:', error);
    throw error;
  }
};