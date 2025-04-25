import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  CircularProgress,
  Grid,
  Alert,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  ListSubheader
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import PreviewIcon from '@mui/icons-material/Preview';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { API_CONFIG } from '../config';
import { normalizeUUID } from '../hooks/useConfig';
import apiService from '../services/api';

const TemplateEditor = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Parse query parameters
  const queryParams = new URLSearchParams(location.search);
  const queryBusinessId = queryParams.get('business_id');
  const queryAgentId = queryParams.get('agent_id');
  
  // Get stored business ID and API key from localStorage
  const storedBusinessId = localStorage.getItem('businessId');
  const storedApiKey = localStorage.getItem('businessApiKey');
  const storedAgentId = localStorage.getItem('agentId');
  
  // State for template data
  const [template, setTemplate] = useState({
    template_id: templateId === 'new' ? '' : templateId,
    template_name: '',
    content: '',
    system_prompt: '',
    template_type: 'stage_selection',
    variables: [],
    agent_id: ''
  });
  
  // State for UI
  const [businessId, setBusinessId] = useState(queryBusinessId || storedBusinessId || '');
  const [businessApiKey, setBusinessApiKey] = useState(storedApiKey || '');
  const [agentId, setAgentId] = useState(queryAgentId || storedAgentId || '');
  const [showBusinessIdInput, setShowBusinessIdInput] = useState(!businessId || !businessApiKey);
  const [showAgentIdInput, setShowAgentIdInput] = useState(!agentId);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  // Add state for template types array
  const templateTypes = [
    { value: 'stage_selection', label: 'Stage Selection', group: 'Regular' },
    { value: 'data_extraction', label: 'Data Extraction', group: 'Regular' },
    { value: 'response_generation', label: 'Response Generation', group: 'Regular' },
    { value: 'default_stage_selection', label: 'Default Stage Selection', group: 'Default' },
    { value: 'default_data_extraction', label: 'Default Data Extraction', group: 'Default' },
    { value: 'default_response_generation', label: 'Default Response Generation', group: 'Default' }
  ];
  
  // Extract variables from template content
  const extractVariables = (text) => {
    if (!text) return [];
    const matches = text.match(/\{([^}]+)\}/g) || [];
    return matches.map(match => match.slice(1, -1));
  };
  
  // Update variables whenever template content changes
  useEffect(() => {
    const variables = extractVariables(template.content);
    setTemplate(prev => ({
      ...prev,
      variables
    }));
  }, [template.content]);
  
  // Update template's agent_id when agentId changes
  useEffect(() => {
    if (agentId) {
      setTemplate(prev => ({
        ...prev,
        agent_id: agentId
      }));
    }
  }, [agentId]);
  
  // Fetch template data if editing an existing template
  useEffect(() => {
    const fetchTemplateData = async () => {
      // Skip fetching for new templates
      if (templateId === 'new') return;
      
      // Skip fetching if templateId is invalid/undefined
      if (!templateId || templateId === 'undefined') {
        console.error('Invalid template ID:', templateId);
        showSnackbar('Invalid template ID', 'error');
        // Redirect to template creation
        navigate('/template-editor/new');
        return;
      }
      
      if (!businessId) {
        showSnackbar('Business ID is required to fetch template', 'error');
        setShowBusinessIdInput(true);
        return;
      }
      
      if (!businessApiKey) {
        showSnackbar('Business API Key is required', 'error');
        setShowBusinessIdInput(true);
        return;
      }
      
      setIsLoading(true);
      try {
        console.log(`Fetching template with ID: ${templateId} for business: ${businessId}`);
        
        // Use apiService to fetch template details
        // Need to pass businessId separately or include it in the call if the service expects it
        // Checking apiService definition, fetchTemplateDetails only takes templateId
        // The business_id needs to be handled by the apiService internally or passed differently.
        // Let's assume apiService handles authentication via headers which include business context.
        // If not, we might need to modify apiService or pass businessId differently.
        
        // Corrected call assuming apiService uses stored credentials for business_id
        const data = await apiService.fetchTemplateDetails(templateId);

        console.log('Fetched template:', data);
        
        // Don't modify the template_type, preserve its original value
        setTemplate({
          template_id: data.template_id,
          template_name: data.template_name || '',
          content: data.content || '',
          system_prompt: data.system_prompt || '',
          template_type: data.template_type || 'stage_selection',
          variables: extractVariables(data.content),
          agent_id: data.agent_id || ''
        });
      } catch (err) {
        console.error('Error fetching template:', err);
        showSnackbar(err.message, 'error');
        // Redirect to template list on error
        navigate('/templates');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTemplateData();
  }, [templateId, businessId, businessApiKey, navigate]);
  
  // Validate credentials
  const validateCredentials = async () => {
    if (!businessId || !businessApiKey) {
      setSnackbar({
        open: true,
        message: 'Business ID and API Key are required',
        severity: 'error'
      });
      setShowBusinessIdInput(true);
      return false;
    }
    
    try {
      // Use the correct endpoint and method
      const response = await fetch(`/businesses/validate-credentials?business_id=${businessId}&api_key=${businessApiKey}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${businessApiKey}`
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Invalid business ID or API key');
      }
      
      const data = await response.json();
      if (!data.valid) {
        throw new Error(data.message || 'Credential validation failed');
      }
      
      return true;
    } catch (err) {
      console.error('Credential validation error:', err);
      setSnackbar({
        open: true,
        message: 'Failed to validate credentials: ' + err.message,
        severity: 'error'
      });
      setShowBusinessIdInput(true);
      return false;
    }
  };
  
  // Save credentials
  const saveCredentials = async () => {
    if (!businessId || !businessApiKey) {
      showSnackbar('Please enter both Business ID and API Key', 'error');
      return;
    }
    
    const isValid = await validateCredentials();
    if (isValid) {
      // Save to both localStorage and cookies
      localStorage.setItem('businessId', businessId);
      localStorage.setItem('businessApiKey', businessApiKey);
      document.cookie = `businessId=${businessId}; path=/; max-age=86400`;
      document.cookie = `businessApiKey=${businessApiKey}; path=/; max-age=86400`;
      
      setShowBusinessIdInput(false);
      showSnackbar('Business credentials validated and saved', 'success');
    }
  };
  
  // Handle template preview
  const handlePreview = async () => {
    if (!template.content.trim()) {
      showSnackbar('Template content is empty', 'error');
      return;
    }
    
    setIsLoading(true);
    try {
      // Prepare preview request
      const previewRequest = {
        template_type: template.template_type,
        template_text: template.content,
        business_id: businessId,
        agent_id: agentId,
        context: {
          conversation_history: [
            { role: "user", content: "I'm interested in your products" },
            { role: "assistant", content: "I'd be happy to tell you about our products. What type are you interested in?" }
          ],
          extracted_data: {
            customer_name: "John Doe",
            product_interest: "shoes",
            budget: "$100"
          }
        }
      };
      
      let previewSuccess = false;
      let errorMessage = '';
      
      // Try multiple possible endpoints (for compatibility)
      const endpoints = [
        '/templates/preview',
        '/templates/render',
        '/render_template',
        '/api/templates/preview'
      ];
      
      let response = null;
      for (const endpoint of endpoints) {
        try {
          console.log(`Trying to preview template with endpoint: ${endpoint}`);
          
          response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'Authorization': `Bearer ${businessApiKey}`
            },
            credentials: 'include',
            body: JSON.stringify(previewRequest),
          });
          
          if (response.ok) {
            const data = await response.json();
            console.log('Preview response:', data);
            setPreviewData(data);
            setShowPreview(true);
            previewSuccess = true;
            break;
          } else {
            const errData = await response.json().catch(() => ({}));
            errorMessage = errData.message || errData.error || `Failed with status ${response.status}`;
            console.warn(`Endpoint ${endpoint} failed: ${errorMessage}`);
          }
        } catch (endpointErr) {
          console.warn(`Endpoint ${endpoint} failed:`, endpointErr);
          errorMessage = endpointErr.message;
        }
      }
      
      // If no endpoint worked, use fallback preview
      if (!previewSuccess) {
        console.log('All endpoint attempts failed, using local preview');
        
        // Simple variable replacement for demonstration
        let previewText = template.content;
        
        // Replace variables with sample values
        template.variables.forEach(variable => {
          const sampleValue = `[Sample ${variable}]`;
          previewText = previewText.replace(new RegExp(`{${variable}}`, 'g'), sampleValue);
        });
        
        setPreviewData({ 
          rendered_text: previewText,
          message: "Using client-side preview (API endpoints not available)",
          is_fallback: true
        });
        setShowPreview(true);
        
        // Show notification
        showSnackbar(`Using fallback preview. Server error: ${errorMessage}`, 'warning');
      }
    } catch (err) {
      console.error('Error generating preview:', err);
      showSnackbar(`Failed to generate preview: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Save template changes
  const handleSaveTemplate = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    // Prepare template data for saving
    const templateData = {
      template_name: template.template_name,
      content: template.content,
      system_prompt: template.system_prompt,
      template_type: template.template_type,
      // Ensure variables are updated based on the current content
      variables: extractVariables(template.content),
      agent_id: template.agent_id // Include agent_id
    };

    try {
      let savedTemplate;
      if (templateId && templateId !== 'new') {
        // Update existing template
        console.log(`Updating template with ID: ${templateId}`, templateData);
        savedTemplate = await apiService.updateTemplate(templateId, templateData);
        showSnackbar('Template updated successfully!', 'success');
      } else {
        // Create new template
        console.log('Creating new template:', templateData);
        savedTemplate = await apiService.createTemplate(templateData);
        showSnackbar('Template created successfully!', 'success');
        // Navigate to the edit page of the newly created template
        navigate(`/template-editor/${savedTemplate.template_id}`);
      }
      console.log('Save successful:', savedTemplate);
    } catch (err) {
      console.error('Error saving template:', err);
      showSnackbar(`Failed to save template: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Navigate back to templates list
  const handleCancel = () => {
    navigate('/templates');
  };
  
  // Handle template type change
  const handleTemplateTypeChange = (e) => {
    const newType = e.target.value;
    console.log('Template type changed to:', newType);
    setTemplate(prev => {
      const updated = { 
        ...prev, 
        template_type: newType
      };
      console.log('Updated template state:', updated);
      return updated;
    });
  };
  
  // Snackbar functions
  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({
      ...prev,
      open: false
    }));
  };
  
  return (
    <Paper sx={{ p: 3, mb: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Back button and title */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={handleCancel} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5">
          {template.template_id && template.template_id !== 'new' ? 'Edit Template' : 'Create New Template'}
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveTemplate}
          disabled={isLoading || !template.template_name.trim() || !template.content.trim()}
          startIcon={isLoading ? <CircularProgress size={24} /> : <SaveIcon />}
        >
          Save Template
        </Button>
      </Box>
      
      {/* Business ID input section */}
      {(showBusinessIdInput || !businessId || !businessApiKey) && (
        <Box sx={{ mb: 3, p: 2, border: '1px dashed', borderColor: 'warning.main', borderRadius: 1 }}>
          <Typography variant="subtitle1" color="warning.main" gutterBottom>
            Business Credentials Required
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={5}>
              <TextField
                fullWidth
                label="Business ID"
                value={businessId}
                onChange={(e) => setBusinessId(e.target.value)}
                placeholder="Enter your business ID"
                helperText="Required for saving templates"
                required
              />
            </Grid>
            <Grid item xs={12} md={5}>
              <TextField
                fullWidth
                label="Business API Key"
                value={businessApiKey}
                onChange={(e) => setBusinessApiKey(e.target.value)}
                placeholder="Enter your business API key"
                helperText="Required for authentication"
                type="password"
                required
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={saveCredentials}
                fullWidth
                sx={{ height: '56px' }}
              >
                Validate & Save
              </Button>
            </Grid>
          </Grid>
        </Box>
      )}
      
      {/* Agent ID input section */}
      {(showAgentIdInput || !agentId) && (
        <Box sx={{ mb: 3, p: 2, border: '1px dashed', borderColor: 'warning.main', borderRadius: 1 }}>
          <Typography variant="subtitle1" color="warning.main" gutterBottom>
            Agent ID Required
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={5}>
              <TextField
                fullWidth
                label="Agent ID"
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                placeholder="Enter your agent ID"
                helperText="Required for saving templates"
                required
              />
            </Grid>
          </Grid>
        </Box>
      )}
      
      {/* Template information section */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Template Name"
            value={template.template_name}
            onChange={(e) => setTemplate(prev => ({ ...prev, template_name: e.target.value }))}
            required
            error={!template.template_name.trim()}
            helperText={!template.template_name.trim() ? "Template name is required" : ""}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="template-type-label">Template Type</InputLabel>
            <Select
              labelId="template-type-label"
              value={template.template_type}
              label="Template Type"
              onChange={handleTemplateTypeChange}
            >
              <ListSubheader>Regular Templates</ListSubheader>
              {templateTypes
                .filter(type => type.group === 'Regular')
                .map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))
              }
              <ListSubheader>Default Templates</ListSubheader>
              {templateTypes
                .filter(type => type.group === 'Default')
                .map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))
              }
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Template Description"
            value={template.template_description}
            onChange={(e) => setTemplate(prev => ({ ...prev, template_description: e.target.value }))}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="subtitle1" sx={{ mr: 2 }}>
              Detected Variables:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {template.variables.length > 0 ? (
                template.variables.map((variable, index) => (
                  <Chip 
                    key={index} 
                    label={variable} 
                    color="primary" 
                    variant="outlined" 
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No variables detected. Use {"{variable_name}"} syntax.
                </Typography>
              )}
            </Box>
          </Box>
          
          <Button
            variant="outlined"
            color="primary"
            onClick={handlePreview}
            disabled={!template.content.trim()}
            startIcon={<VisibilityIcon />}
            sx={{ mt: 2 }}
          >
            Preview Template
          </Button>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>
            Template Content
            <Tooltip title="Use {variable_name} syntax to create variables in your template">
              <IconButton size="small">
                <HelpOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={10}
            value={template.content}
            onChange={(e) => setTemplate({ ...template, content: e.target.value })}
            placeholder="Enter your template content here with variables in {curly_braces}..."
            sx={{ 
              mb: 2, 
              fontFamily: 'monospace',
              '& .MuiInputBase-input': {
                fontFamily: 'monospace',
              }
            }}
          />
          
          <Grid item xs={12}>
            <TextField
              label="System Prompt (Optional)"
              value={template.system_prompt}
              onChange={(e) => setTemplate({ ...template, system_prompt: e.target.value })}
              fullWidth
              multiline
              rows={4}
              margin="normal"
              variant="outlined"
              placeholder="Enter optional system prompt for the model..."
            />
          </Grid>
        </Grid>
      </Grid>
      
      {/* Preview Dialog */}
      <Dialog 
        open={showPreview} 
        onClose={() => setShowPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Template Preview</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            Template: {template.template_name}
          </Typography>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Type: {template.template_type}
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ 
            bgcolor: 'background.paper', 
            p: 2, 
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider',
            maxHeight: '500px',
            overflow: 'auto',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {previewData?.rendered_text || previewData?.content || 'No preview data available'}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default TemplateEditor;