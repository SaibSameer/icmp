import { API_CONFIG } from '../config';
import { getAuthHeaders } from './authService';
import { normalizeUUID } from '../hooks/useConfig';

/**
 * Template API client service
 * Handles all template-related API operations
 */
class TemplateApiService {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.endpoint = API_CONFIG.ENDPOINTS.TEMPLATES;
  }

  /**
   * Fetch all templates for a business
   * @param {string} businessId - The business ID
   * @param {string} agentId - Optional agent ID
   * @param {Object} options - Additional options (templateType, isDefault)
   * @returns {Promise<Array>} List of templates
   */
  async fetchTemplates(businessId, agentId, options = {}) {
    try {
      const normalizedBusinessId = normalizeUUID(businessId);
      const normalizedAgentId = agentId ? normalizeUUID(agentId) : null;

      console.log(`Fetching templates for business: ${normalizedBusinessId}, agent: ${normalizedAgentId}`);
      
      const params = new URLSearchParams({
        business_id: normalizedBusinessId,
      });

      if (normalizedAgentId) {
        params.append('agent_id', normalizedAgentId);
      }
      
      if (options.templateType) {
        params.append('template_type', options.templateType);
      }
      
      if (options.isDefault !== undefined) {
        params.append('is_default', options.isDefault);
      }

      const response = await fetch(`${this.baseUrl}${this.endpoint}?${params.toString()}`, {
        method: 'GET',
        credentials: 'include',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch templates');
      }

      const data = await response.json();
      console.log("Retrieved templates:", data);
      return Array.isArray(data) ? data : [];

    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  }

  /**
   * Get a single template by ID
   * @param {string} templateId - The template ID
   * @param {string} businessId - The business ID
   * @returns {Promise<Object>} Template details
   */
  async getTemplate(templateId, businessId) {
    try {
      const normalizedBusinessId = normalizeUUID(businessId);
      
      console.log(`Fetching template ${templateId} for business: ${normalizedBusinessId}`);
      
      const params = new URLSearchParams({
        business_id: normalizedBusinessId
      });

      const response = await fetch(`${this.baseUrl}${this.endpoint}/${templateId}?${params.toString()}`, {
        method: 'GET',
        credentials: 'include',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch template');
      }

      const data = await response.json();
      console.log("Retrieved template:", data);
      return data;

    } catch (error) {
      console.error('Error fetching template:', error);
      throw error;
    }
  }

  /**
   * Create a new template
   * @param {Object} templateData - The template data
   * @returns {Promise<Object>} Created template
   */
  async createTemplate(templateData) {
    try {
      // Make sure business_id and agent_id are normalized
      const normalizedData = {
        ...templateData,
        business_id: normalizeUUID(templateData.business_id),
        agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null
      };
      
      console.log('Creating template with data:', {
        original: templateData.business_id,
        normalized: normalizedData.business_id
      });

      const response = await fetch(`${this.baseUrl}${this.endpoint}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(normalizedData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to create template');
      }

      const data = await response.json();
      console.log("Created template:", data);
      return data;

    } catch (error) {
      console.error('Error creating template:', error);
      throw error;
    }
  }

  /**
   * Update an existing template
   * @param {string} templateId - The template ID
   * @param {Object} updateData - The data to update
   * @returns {Promise<Object>} Updated template
   */
  async updateTemplate(templateId, updateData) {
    try {
      // Make sure business_id and agent_id are normalized
      const normalizedData = {
        ...updateData,
        business_id: updateData.business_id ? normalizeUUID(updateData.business_id) : undefined,
        agent_id: updateData.agent_id ? normalizeUUID(updateData.agent_id) : undefined
      };
      
      console.log(`Updating template ${templateId}:`, {
        original: updateData.business_id,
        normalized: normalizedData.business_id
      });

      const response = await fetch(`${this.baseUrl}${this.endpoint}/${templateId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(normalizedData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update template');
      }

      const data = await response.json();
      console.log("Updated template:", data);
      return data;

    } catch (error) {
      console.error('Error updating template:', error);
      throw error;
    }
  }

  /**
   * Delete a template
   * @param {string} templateId - The template ID
   * @param {string} businessId - The business ID
   * @returns {Promise<void>}
   */
  async deleteTemplate(templateId, businessId) {
    try {
      const normalizedBusinessId = normalizeUUID(businessId);
      
      console.log(`Deleting template ${templateId} for business: ${normalizedBusinessId}`);
      
      const params = new URLSearchParams({
        business_id: normalizedBusinessId
      });

      const response = await fetch(`${this.baseUrl}${this.endpoint}/${templateId}?${params.toString()}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to delete template');
      }

      console.log(`Template ${templateId} deleted successfully`);
      return true;

    } catch (error) {
      console.error('Error deleting template:', error);
      throw error;
    }
  }

  /**
   * Duplicate a template
   * @param {Object} templateData - The template data to duplicate
   * @returns {Promise<Object>} Created template
   */
  async duplicateTemplate(templateData) {
    try {
      // Make sure business_id and agent_id are normalized
      const normalizedData = {
        ...templateData,
        business_id: normalizeUUID(templateData.business_id),
        agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null,
        template_name: `${templateData.template_name} (Copy)`
      };
      
      console.log('Duplicating template as:', normalizedData);
      return await this.createTemplate(normalizedData);
    } catch (error) {
      console.error('Error duplicating template:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const templateApi = new TemplateApiService();