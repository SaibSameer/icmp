import { API_CONFIG, AUTH_CONFIG } from '../config';
import { getAuthHeaders } from './authService';
import { normalizeUUID } from '../hooks/useConfig';
import axios from 'axios';

const templateService = {
    // Template Variables
    getTemplateVariables: async () => {
        try {
            console.log('Starting getTemplateVariables...');
            const headers = getAuthHeaders();
            console.log('Auth headers:', headers);
            console.log('API URL:', `${API_CONFIG.BASE_URL}/api/template-variables/available/`);
            
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/template-variables/available/`, {
                method: 'GET',
                credentials: 'include',
                headers: headers
            });

            console.log('API Response status:', response.status);
            console.log('API Response headers:', Object.fromEntries(response.headers.entries()));

            if (!response.ok) {
                const errorData = await response.json();
                console.error('API Error response:', errorData);
                throw new Error(errorData.message || 'Failed to fetch template variables');
            }

            const data = await response.json();
            console.log('Raw API response data:', data);

            const normalizedData = data.map(variable => {
                if (typeof variable === 'string') {
                    return {
                        variable_id: variable,
                        variable_name: variable,
                        description: '',
                        example_value: ''
                    };
                }
                return {
                    ...variable,
                    variable_id: variable.id || variable.variable_id,
                    variable_name: variable.name || variable.variable_name,
                    description: variable.description || '',
                    example_value: variable.example || variable.example_value || ''
                };
            });

            console.log('Normalized variables data:', normalizedData);
            return normalizedData;
        } catch (error) {
            console.error('Error in getTemplateVariables:', error);
            console.error('Error stack:', error.stack);
            throw error;
        }
    },

    // Templates
    getTemplates: async (businessId, agentId = null) => {
        try {
            const normalizedBusinessId = normalizeUUID(businessId);
            let url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}?business_id=${normalizedBusinessId}`;
            
            if (agentId) {
                const normalizedAgentId = normalizeUUID(agentId);
                url += `&agent_id=${normalizedAgentId}`;
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
            console.error('Error in getTemplates:', error);
            throw error;
        }
    },

    getTemplate: async (templateId, businessId) => {
        try {
            const normalizedBusinessId = normalizeUUID(businessId);
            const response = await fetch(
                `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}?business_id=${normalizedBusinessId}`,
                {
                    method: 'GET',
                    credentials: 'include',
                    headers: getAuthHeaders()
                }
            );
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to fetch template');
            }

            return await response.json();
        } catch (error) {
            console.error('Error in getTemplate:', error);
            throw error;
        }
    },

    createTemplate: async (templateData) => {
        try {
            const normalizedData = {
                ...templateData,
                business_id: normalizeUUID(templateData.business_id),
                agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null
            };
            
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
    },

    updateTemplate: async (templateId, templateData) => {
        try {
            const normalizedData = {
                ...templateData,
                business_id: normalizeUUID(templateData.business_id),
                agent_id: templateData.agent_id ? normalizeUUID(templateData.agent_id) : null
            };
            
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
    },

    testTemplate: async (businessId, agentId, templateContent) => {
        try {
            const normalizedBusinessId = normalizeUUID(businessId);
            const normalizedAgentId = agentId ? normalizeUUID(agentId) : null;
            
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/template-test`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    business_id: normalizedBusinessId,
                    agent_id: normalizedAgentId,
                    template_content: templateContent,
                    test_mode: true
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to test template');
            }

            return await response.json();
        } catch (error) {
            console.error('Error in testTemplate:', error);
            throw error;
        }
    }
};

export default templateService;