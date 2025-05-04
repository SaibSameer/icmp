import { useState, useEffect, useCallback } from 'react';
import { templateApi } from '../services/templateApi';
import useConfig from './useConfig';
import { normalizeUUID } from './useConfig';

/**
 * Custom hook for managing templates
 * @param {Function} handleSnackbarOpen - Function to show snackbar notifications
 * @param {string} agentId - Optional agent ID
 * @returns {Object} Template management methods and state
 */
export const useTemplates = (handleSnackbarOpen, agentId) => {
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { businessId } = useConfig(); // Get businessId from config
  const normalizedBusinessId = normalizeUUID(businessId);
  const normalizedAgentId = normalizeUUID(agentId);

  // Fetch all templates
  const fetchTemplatesData = useCallback(async (options = {}) => {
    if (!normalizedBusinessId || !normalizedAgentId) {
      setTemplates([]); // Clear templates if no businessId or agentId
      return;
    }

    setIsLoading(true);
    setError(null);
    console.log(`Fetching templates for business ID: ${normalizedBusinessId}, agent ID: ${normalizedAgentId}`);

    try {
      const data = await templateApi.fetchTemplates(normalizedBusinessId, normalizedAgentId, options);
      console.log("Fetched templates:", data);
      // Ensure data is always an array, even if API returns null/undefined
      setTemplates(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching templates:", err);
      const errorMessage = err.message || 'Failed to fetch templates';
      setError(errorMessage);
      setTemplates([]); // Clear templates on error
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error fetching templates: ${errorMessage}`, "error");
      }
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, normalizedAgentId, handleSnackbarOpen]);

  // Get a single template
  const getTemplate = useCallback(async (templateId) => {
    try {
      setIsLoading(true);
      setError(null);
      return await templateApi.getTemplate(templateId, normalizedBusinessId);
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch template';
      setError(errorMessage);
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error fetching template: ${errorMessage}`, "error");
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, handleSnackbarOpen]);

  // Create a new template
  const createTemplate = useCallback(async (templateData) => {
    try {
      setIsLoading(true);
      setError(null);
      const newTemplate = await templateApi.createTemplate({
        ...templateData,
        business_id: normalizedBusinessId
      });
      setTemplates(prev => [...prev, newTemplate]);
      if (handleSnackbarOpen) {
        handleSnackbarOpen("Template created successfully", "success");
      }
      return newTemplate;
    } catch (err) {
      const errorMessage = err.message || 'Failed to create template';
      setError(errorMessage);
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error creating template: ${errorMessage}`, "error");
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, handleSnackbarOpen]);

  // Update a template
  const updateTemplate = useCallback(async (templateId, updateData) => {
    try {
      setIsLoading(true);
      setError(null);
      const updatedTemplate = await templateApi.updateTemplate(templateId, {
        ...updateData,
        business_id: normalizedBusinessId
      });
      setTemplates(prev => 
        prev.map(template => 
          template.template_id === templateId ? updatedTemplate : template
        )
      );
      if (handleSnackbarOpen) {
        handleSnackbarOpen("Template updated successfully", "success");
      }
      return updatedTemplate;
    } catch (err) {
      const errorMessage = err.message || 'Failed to update template';
      setError(errorMessage);
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error updating template: ${errorMessage}`, "error");
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, handleSnackbarOpen]);

  // Delete a template
  const deleteTemplate = useCallback(async (templateId) => {
    try {
      setIsLoading(true);
      setError(null);
      await templateApi.deleteTemplate(templateId, normalizedBusinessId);
      setTemplates(prev => 
        prev.filter(template => template.template_id !== templateId)
      );
      if (handleSnackbarOpen) {
        handleSnackbarOpen("Template deleted successfully", "success");
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete template';
      setError(errorMessage);
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error deleting template: ${errorMessage}`, "error");
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, handleSnackbarOpen]);

  // Duplicate a template
  const duplicateTemplate = useCallback(async (templateData) => {
    try {
      setIsLoading(true);
      setError(null);
      const newTemplate = await templateApi.duplicateTemplate({
        ...templateData,
        business_id: normalizedBusinessId,
        agent_id: normalizedAgentId
      });
      setTemplates(prev => [...prev, newTemplate]);
      if (handleSnackbarOpen) {
        handleSnackbarOpen("Template duplicated successfully", "success");
      }
      return newTemplate;
    } catch (err) {
      const errorMessage = err.message || 'Failed to duplicate template';
      setError(errorMessage);
      if (handleSnackbarOpen) {
        handleSnackbarOpen(`Error duplicating template: ${errorMessage}`, "error");
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [normalizedBusinessId, normalizedAgentId, handleSnackbarOpen]);

  // Fetch templates on mount and when dependencies change
  useEffect(() => {
    fetchTemplatesData();
  }, [fetchTemplatesData]);

  return {
    templates,
    isLoading,
    error,
    refreshTemplates: fetchTemplatesData,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    duplicateTemplate
  };
};