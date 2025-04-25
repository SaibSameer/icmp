import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../../config';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';

function AddStageForm() {
    // --- Routing & Context ---
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const agentIdParam = queryParams.get('agent_id'); // Get agent context ('uuid' or 'null')
    const navigate = useNavigate();

    // --- State ---
    const [formData, setFormData] = useState({
        stage_name: '',
        stage_description: 'Default description',
        stage_type: 'conversation',
        stage_selection_template_id: '',
        data_extraction_template_id: '',
        response_generation_template_id: ''
    });
    const [availableTemplates, setAvailableTemplates] = useState({ selection: [], extraction: [], generation: [] });
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState(null);
    const [contextAgentName, setContextAgentName] = useState('General');

    // Get stored credentials
    const getStoredCredentials = () => {
        return {
            businessId: localStorage.getItem('businessId') || '',
            businessApiKey: localStorage.getItem('businessApiKey') || ''
        };
    };

    // --- Effects ---
    // 1. Determine context agent name
    useEffect(() => {
        setContextAgentName(agentIdParam === 'null' ? 'General' : `Agent ${agentIdParam}`);
    }, [agentIdParam]);

    // 2. Fetch available templates
    useEffect(() => {
        const fetchTemplates = async () => {
            setError(null);
            setIsLoading(true);
            console.log("Fetching available templates...");
            
            const { businessId, businessApiKey } = getStoredCredentials();
            
            if (!businessId || !businessApiKey) {
                setError('Authentication required. Please log in.');
                setIsLoading(false);
                return;
            }
            
            // Organize templates by type for dropdowns
            const organized = { 
                selection: [], 
                extraction: [], 
                generation: [] 
            };
            
            try {
                // Step 1: Fetch regular templates first
                const regularResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}?business_id=${businessId}`, {
                    method: 'GET',
                    headers: { 
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${businessApiKey}`
                    }
                });
                
                if (!regularResponse.ok) {
                    const errorData = await regularResponse.json().catch(() => ({}));
                    throw new Error(`HTTP error ${regularResponse.status}: ${errorData.message || 'Failed to fetch templates'}`);
                }
                
                const regularTemplates = await regularResponse.json();
                console.log("Regular templates fetched:", regularTemplates);
                
                // Process regular templates
                regularTemplates.forEach(template => {
                    if (template.template_type === 'selection') {
                        organized.selection.push(template);
                    } else if (template.template_type === 'extraction') {
                        organized.extraction.push(template);
                    } else if (template.template_type === 'generation') {
                        organized.generation.push(template);
                    }
                });
                
                // Step 2: Now fetch default templates
                const defaultResponse = await fetch(`${API_CONFIG.BASE_URL}/api/templates/default-templates?business_id=${businessId}`, {
                    method: 'GET',
                    headers: { 
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${businessApiKey}`
                    }
                });
                
                if (!defaultResponse.ok) {
                    const errorData = await defaultResponse.json().catch(() => ({}));
                    throw new Error(`HTTP error ${defaultResponse.status}: ${errorData.message || 'Failed to fetch default templates'}`);
                }
                
                const defaultTemplates = await defaultResponse.json();
                console.log("Default templates fetched:", defaultTemplates);
                
                // Process default templates
                defaultTemplates.forEach(template => {
                    if (template.template_type === 'selection') {
                        organized.selection.push(template);
                    } else if (template.template_type === 'extraction') {
                        organized.extraction.push(template);
                    } else if (template.template_type === 'generation') {
                        organized.generation.push(template);
                    }
                });
                
                // Sort templates by name
                organized.selection.sort((a, b) => a.template_name.localeCompare(b.template_name));
                organized.extraction.sort((a, b) => a.template_name.localeCompare(b.template_name));
                organized.generation.sort((a, b) => a.template_name.localeCompare(b.template_name));
                
                console.log("Organized templates:", organized);
                setAvailableTemplates(organized);
                
                // Set default templates if available
                const defaultSelection = organized.selection.find(t => t.template_name.toLowerCase().includes('default'));
                const defaultExtraction = organized.extraction.find(t => t.template_name.toLowerCase().includes('default'));
                const defaultGeneration = organized.generation.find(t => t.template_name.toLowerCase().includes('default'));
                
                if (defaultSelection || defaultExtraction || defaultGeneration) {
                    setFormData(prev => ({
                        ...prev,
                        stage_selection_template_id: defaultSelection ? defaultSelection.template_id : '',
                        data_extraction_template_id: defaultExtraction ? defaultExtraction.template_id : '',
                        response_generation_template_id: defaultGeneration ? defaultGeneration.template_id : ''
                    }));
                }
                
            } catch (err) {
                console.error("Error fetching templates:", err);
                setError(err.message || "Failed to load templates. Please try again later.");
            } finally {
                setIsLoading(false);
            }
        };
        
        fetchTemplates();
    }, []);

    // --- Handlers ---
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        console.log(`Field ${name} changed to: ${value}`);
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setError(null);
        
        const { businessId, businessApiKey } = getStoredCredentials();
        
        if (!businessId || !businessApiKey) {
            setError('Authentication required. Please log in.');
            setIsSaving(false);
            return;
        }
        
        // Log the form state to verify values
        console.log("Form state before submission:", formData);
        
        try {
            const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STAGES}?business_id=${businessId}`;
            const method = 'POST';
            
            console.log(`Submitting stage data to ${url} using ${method}`);
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${businessApiKey}`
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.message || 'Failed to save stage'}`);
            }
            
            const result = await response.json();
            console.log(`Stage created successfully:`, result);
            
            // Navigate to the stage management page
            navigate('/stage-management');
            
        } catch (err) {
            console.error(`Error creating stage:`, err);
            setError(err.message || `An unexpected error occurred while creating the stage.`);
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancel = () => {
        navigate('/stage-management');
    };

    // --- Render ---
    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box component="form" onSubmit={handleSubmit} noValidate>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Add New Stage
                </Typography>
                
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}
                
                <Grid container spacing={3}>
                    {/* Basic Information */}
                    <Grid item xs={12}>
                        <Typography variant="subtitle1" gutterBottom>
                            Basic Information
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                        <TextField
                            required
                            fullWidth
                            id="stage_name"
                            name="stage_name"
                            label="Stage Name"
                            value={formData.stage_name}
                            onChange={handleInputChange}
                            error={!formData.stage_name}
                            helperText={!formData.stage_name ? "Stage name is required" : ""}
                        />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                            <InputLabel id="stage_type_label">Stage Type</InputLabel>
                            <Select
                                labelId="stage_type_label"
                                id="stage_type"
                                name="stage_type"
                                value={formData.stage_type}
                                onChange={handleInputChange}
                                label="Stage Type"
                            >
                                <MenuItem value="conversation">Conversation</MenuItem>
                                <MenuItem value="response">Response</MenuItem>
                                <MenuItem value="form">Form</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    <Grid item xs={12}>
                        <TextField
                            fullWidth
                            id="stage_description"
                            name="stage_description"
                            label="Stage Description"
                            multiline
                            rows={3}
                            value={formData.stage_description}
                            onChange={handleInputChange}
                        />
                    </Grid>
                    
                    {/* Template Selection */}
                    <Grid item xs={12}>
                        <Typography variant="subtitle1" gutterBottom>
                            Template Selection
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                    </Grid>
                    
                    <Grid item xs={12}>
                        <FormControl fullWidth>
                            <InputLabel id="stage_selection_template_label">Stage Selection Template</InputLabel>
                            <Select
                                labelId="stage_selection_template_label"
                                id="stage_selection_template_id"
                                name="stage_selection_template_id"
                                value={formData.stage_selection_template_id}
                                onChange={handleInputChange}
                                label="Stage Selection Template"
                            >
                                {availableTemplates.selection.length === 0 ? (
                                    <MenuItem value="">
                                        <em>No templates available</em>
                                    </MenuItem>
                                ) : (
                                    availableTemplates.selection.map(template => (
                                        <MenuItem key={template.template_id} value={template.template_id}>
                                            {template.template_name}
                                        </MenuItem>
                                    ))
                                )}
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    <Grid item xs={12}>
                        <FormControl fullWidth>
                            <InputLabel id="data_extraction_template_label">Data Extraction Template</InputLabel>
                            <Select
                                labelId="data_extraction_template_label"
                                id="data_extraction_template_id"
                                name="data_extraction_template_id"
                                value={formData.data_extraction_template_id}
                                onChange={handleInputChange}
                                label="Data Extraction Template"
                            >
                                {availableTemplates.extraction.length === 0 ? (
                                    <MenuItem value="">
                                        <em>No templates available</em>
                                    </MenuItem>
                                ) : (
                                    availableTemplates.extraction.map(template => (
                                        <MenuItem key={template.template_id} value={template.template_id}>
                                            {template.template_name}
                                        </MenuItem>
                                    ))
                                )}
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    <Grid item xs={12}>
                        <FormControl fullWidth>
                            <InputLabel id="response_generation_template_label">Response Generation Template</InputLabel>
                            <Select
                                labelId="response_generation_template_label"
                                id="response_generation_template_id"
                                name="response_generation_template_id"
                                value={formData.response_generation_template_id}
                                onChange={handleInputChange}
                                label="Response Generation Template"
                            >
                                {availableTemplates.generation.length === 0 ? (
                                    <MenuItem value="">
                                        <em>No templates available</em>
                                    </MenuItem>
                                ) : (
                                    availableTemplates.generation.map(template => (
                                        <MenuItem key={template.template_id} value={template.template_id}>
                                            {template.template_name}
                                        </MenuItem>
                                    ))
                                )}
                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
                
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="outlined"
                        onClick={handleCancel}
                        sx={{ mr: 2 }}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={isSaving || !formData.stage_name || !formData.stage_description}
                    >
                        {isSaving ? 'Saving...' : 'Create Stage'}
                    </Button>
                </Box>
            </Paper>
        </Box>
    );
}

export default AddStageForm;