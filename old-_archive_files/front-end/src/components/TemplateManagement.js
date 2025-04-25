import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    TextField, Button, Typography, Card, CardContent, Box, TextareaAutosize,
    Select, MenuItem, InputLabel, FormControl, Grid, Paper, Divider, Tab, Tabs, Alert, List, ListItem, ListItemText, ListItemSecondaryAction, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, Snackbar, Container, Tooltip, ListSubheader
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SaveIcon from '@mui/icons-material/Save';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import TemplateSection from './TemplateSection';
import AddIcon from '@mui/icons-material/Add';
import FilterListIcon from '@mui/icons-material/FilterList';
import StarIcon from '@mui/icons-material/Star';
import { normalizeUUID } from '../hooks/useConfig';
import { createTemplate, updateTemplate, deleteTemplate, fetchTemplates as fetchTemplatesService, duplicateTemplate } from '../services/templateService';

function TemplateManagement({ templateID, setTemplateID, availableVariable = [], setAvailableVariable, selectedVariable, setSelectedVariable, handleTemplateSelection, handleVariableSelection, addVariableToTemplate, templateName, setTemplateName, templateContent, setTemplateContent, templateSystemPrompt, setTemplateSystemPrompt, templateOutput, createTemplate, fetchTemplates, handleSnackbarOpen, handleSaveDefaultTemplate, apiKey, setTemplateOutput }) {
    const navigate = useNavigate();
    const location = useLocation();
    const [templates, setTemplates] = useState([]);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [templateType, setTemplateType] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [activeTab, setActiveTab] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [editingTemplate, setEditingTemplate] = useState({
        template_id: '',
        template_name: '',
        content: '',
        system_prompt: '',
        template_type: '',
        variables: []
    });
    const [filterType, setFilterType] = useState('all');
    const [showBusinessIdInput, setShowBusinessIdInput] = useState(!apiKey || !templateID);
    const [businessId, setBusinessId] = useState(templateID || '');
    const [businessApiKey, setBusinessApiKey] = useState(apiKey || '');
    const [agentId, setAgentId] = useState('');
    const [filteredTemplates, setFilteredTemplates] = useState([]);
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });
    const [showAgentIdInput, setShowAgentIdInput] = useState(!agentId);

    // Define template types array for dropdowns and filtering
    const templateTypes = [
        { value: 'stage_selection', label: 'Stage Selection', group: 'Regular' },
        { value: 'data_extraction', label: 'Data Extraction', group: 'Regular' },
        { value: 'response_generation', label: 'Response Generation', group: 'Regular' },
        { value: 'default_stage_selection', label: 'Default Stage Selection', group: 'Default' },
        { value: 'default_data_extraction', label: 'Default Data Extraction', group: 'Default' },
        { value: 'default_response_generation', label: 'Default Response Generation', group: 'Default' }
    ];

    // Parse query parameters if any
    const queryParams = new URLSearchParams(window.location.search);
    const queryBusinessId = queryParams.get('business_id');
    const queryAgentId = queryParams.get('agent_id');
    
    // Get stored credentials from localStorage
    const storedBusinessId = localStorage.getItem('businessId');
    const storedApiKey = localStorage.getItem('businessApiKey');
    const storedAgentId = localStorage.getItem('agentId');
    
    // Update state with query params and localStorage values
    useEffect(() => {
        // Update businessId if query param or localStorage has a value
        if (queryBusinessId || storedBusinessId) {
            setBusinessId(queryBusinessId || storedBusinessId);
        }
        
        // Update businessApiKey if localStorage has a value
        if (storedApiKey) {
            setBusinessApiKey(storedApiKey);
        }
        
        // Update agentId if query param or localStorage has a value
        if (queryAgentId || storedAgentId) {
            setAgentId(queryAgentId || storedAgentId);
        }
        
        // Update visibility of input fields
        setShowBusinessIdInput(!businessId || !businessApiKey);
        setShowAgentIdInput(!agentId);
    }, [queryBusinessId, storedBusinessId, storedApiKey, queryAgentId, storedAgentId]);
    
    // Initialize filteredTemplates when templates change
    useEffect(() => {
        setFilteredTemplates(templates);
    }, [templates]);
    
    // Effect to fetch templates on mount
    useEffect(() => {
        if (businessId && agentId) {
            console.log("TemplateManagement.js - Fetching templates with:", { businessId, agentId });
            if (typeof fetchTemplates === 'function') {
                fetchTemplates();
            } else {
                // If fetchTemplates is not a prop, use the internal implementation
                fetchTemplatesInternal();
            }
        }
    }, [businessId, agentId, fetchTemplates]);
    
    // Internal implementation of fetchTemplates
    const fetchTemplatesInternal = async () => {
        if (!businessId) {
            showSnackbar('Business ID is required to fetch templates', 'error');
            setShowBusinessIdInput(true);
            setIsLoading(false);
            return;
        }
        
        if (!agentId) {
            showSnackbar('Agent ID is required to fetch templates', 'error');
            setShowAgentIdInput(true);
            setIsLoading(false);
            return;
        }
        
        if (!businessApiKey) {
            showSnackbar('Business API Key is required to fetch templates', 'error');
            setShowBusinessIdInput(true);
            setIsLoading(false);
            return;
        }
        
        setIsLoading(true);
        try {
            // Use the template service instead of direct fetch
            const data = await fetchTemplatesService(businessId, agentId);
            console.log('Fetched templates (raw):', data);
            
            // Normalize the templates data to ensure all needed fields exist
            const normalizedTemplates = Array.isArray(data) ? data.map(template => ({
                template_id: template.template_id || template.id || `temp-${Math.random().toString(36).substring(2, 9)}`,
                template_name: template.template_name || 'Unnamed Template',
                content: template.content || '',
                system_prompt: template.system_prompt || '',
                template_type: template.template_type || 'Unknown Type',
                variables: extractVariablesFromContent(template.content || '')
            })) : [];
            
            console.log('Normalized templates:', normalizedTemplates);
            
            setTemplates(normalizedTemplates);
            setFilteredTemplates(normalizedTemplates);
            
            // Show message about number of templates loaded
            showSnackbar(`${normalizedTemplates.length} templates loaded successfully`, 'success');
        } catch (err) {
            console.error('Error fetching templates:', err);
            showSnackbar(err.message, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        // TODO: Implement API endpoint to retrieve available variables
        const mockVariables = ['variable1', 'variable2', 'variable3'];
        if (typeof setAvailableVariable === 'function') {
            setAvailableVariable(mockVariables);
        }
    }, [setAvailableVariable]);

    const handleCreateTemplate = async () => {
        try {
            if (!templateName || !templateContent || !templateType) {
                setErrorMessage('Template name, content, and type are required');
                return;
            }
            
            // Use the template service instead of direct fetch
            const templateData = {
                template_name: templateName,
                content: templateContent,
                system_prompt: templateSystemPrompt || '',
                template_type: templateType,
                business_id: businessId,
                agent_id: agentId
            };
            
            await createTemplate(templateData);
            
            // Reset form
            setTemplateName('');
            setTemplateContent('');
            setTemplateType('');
            
            // Refresh templates
            fetchTemplates();
            
            setSuccessMessage('Template created successfully');
            
            // Clear success message after 3 seconds
            setTimeout(() => {
                setSuccessMessage('');
            }, 3000);
        } catch (error) {
            setErrorMessage(error.message);
        }
    };

    const handleUpdateTemplate = async () => {
        try {
            if (!editingTemplate) return;
            
            // Use the template service instead of direct fetch
            const templateData = {
                template_name: editingTemplate.template_name,
                content: editingTemplate.content,
                system_prompt: editingTemplate.system_prompt || '',
                template_type: editingTemplate.template_type,
                business_id: businessId,
                agent_id: agentId
            };
            
            await updateTemplate(editingTemplate.template_id, templateData);
            
            // Close dialog and refresh
            setEditDialogOpen(false);
            fetchTemplates();
            
            // Show success message
            showSnackbar('Template updated successfully', 'success');
        } catch (error) {
            console.error('Error updating template:', error);
            showSnackbar(`Failed to update template: ${error.message}`, 'error');
        }
    };

    const handleDeleteTemplate = async (templateId) => {
        if (!window.confirm('Are you sure you want to delete this template?')) {
            return;
        }
        
        try {
            // Use the template service instead of direct fetch
            await deleteTemplate(templateId, businessId);
            
            // Refresh templates
            fetchTemplates();
            
            // Show success message
            showSnackbar('Template deleted successfully', 'success');
        } catch (error) {
            console.error('Error deleting template:', error);
            showSnackbar(`Failed to delete template: ${error.message}`, 'error');
        }
    };

    const handleDuplicateTemplate = async (template) => {
        try {
            setIsLoading(true);
            
            // Use the template service instead of direct fetch
            const templateData = {
                template_name: template.template_name,
                content: template.content,
                system_prompt: template.system_prompt || '',
                template_type: template.template_type,
                business_id: businessId,
                agent_id: agentId
            };
            
            await duplicateTemplate(templateData);
            
            // Refresh templates
            fetchTemplates();
            
            // Show success message
            showSnackbar(`Template "${template.template_name} (Copy)" created successfully`, 'success');
        } catch (error) {
            console.error('Error duplicating template:', error);
            showSnackbar(`Failed to duplicate template: ${error.message}`, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    const handleEditTemplate = (template) => {
        setEditingTemplate(template);
        setEditDialogOpen(true);
    };

    const handleAddVariable = (variable) => {
        setTemplateContent((prev) => `${prev} {${variable}}`);
    };

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const getFilteredTemplates = () => {
        // If searching by text instead of filtering by type
        if (typeof filterType === 'string' && filterType.length > 0 && !templateTypes.some(t => t.value === filterType)) {
            // This is a text search, not a type filter
            const searchTerm = filterType.toLowerCase();
            return templates.filter(template => 
                (template.template_name && template.template_name.toLowerCase().includes(searchTerm)) ||
                (template.template_description && template.template_description.toLowerCase().includes(searchTerm)) ||
                (template.template_id && template.template_id.toLowerCase().includes(searchTerm)) ||
                (template.template_type && template.template_type.toLowerCase().includes(searchTerm))
            );
        }
        
        // Regular type filtering
        if (filterType === 'all') {
            return templates;
        }
        
        return templates.filter(template => {
            const type = template.template_type;
            // Handle the case where type might be undefined or not a string
            if (!type || typeof type !== 'string') return false;
            return type === filterType;
        });
    };

    const isDefaultTemplate = (type) => {
        return type && typeof type === 'string' && type.startsWith('default_');
    };

    const getTemplateTypeLabel = (type) => {
        if (!type) return 'Unknown Type';
        const found = templateTypes.find(t => t.value === type);
        return found ? found.label : type;
    };

    const handleNavigateToHome = () => {
        navigate('/business');
    };

    const validateCredentials = async () => {
        if (!businessId || !businessApiKey) {
            showSnackbar('Business ID and API Key are required', 'error');
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
            showSnackbar('Failed to validate credentials: ' + err.message, 'error');
            setShowBusinessIdInput(true);
            return false;
        }
    };

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
            
            // Refresh templates
            fetchTemplatesInternal();
        }
    };

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

    const handleCreateNewTemplate = () => {
        let url = `/template-editor/new?business_id=${businessId}`;
        if (agentId) {
            url += `&agent_id=${agentId}`;
        }
        navigate(url);
    };
    
    const handleEditExistingTemplate = (templateId) => {
        // Check for invalid template ID
        if (!templateId || templateId === 'undefined') {
            console.error('Invalid template ID:', templateId);
            showSnackbar('Cannot edit template: Invalid template ID', 'error');
            return;
        }
        
        let url = `/template-editor/${templateId}?business_id=${businessId}`;
        if (agentId) {
            url += `&agent_id=${agentId}`;
        }
        console.log(`Navigating to edit template: ${url}`);
        navigate(url);
    };

    // Effect to check if we need to refresh templates (coming from template editor)
    useEffect(() => {
        const templateUpdated = localStorage.getItem('template_updated');
        const refreshParam = queryParams.get('refresh');
        
        if (templateUpdated === 'true' || refreshParam) {
            // Clear the flag
            localStorage.removeItem('template_updated');
            
            // If we have both business ID and agent ID, fetch templates
            if (businessId && agentId && businessApiKey) {
                console.log("Template was just updated, refreshing templates list");
                setTimeout(() => {
                    fetchTemplatesInternal();
                }, 500); // Small delay to ensure backend has processed
            }
        }
    }, [location, businessId, agentId, businessApiKey]);

    // Effect to extract variables from template text
    useEffect(() => {
        if (editingTemplate.content) {
            const matches = editingTemplate.content.match(/\{([^}]+)\}/g) || [];
            const extractedVariables = matches.map(match => match.substring(1, match.length - 1));
            setEditingTemplate(prev => ({
                ...prev,
                variables: Array.from(new Set(extractedVariables))
            }));
        }
    }, [editingTemplate.content]);

    // Helper to extract variables from content
    const extractVariablesFromContent = (content) => {
        if (!content) return [];
        const matches = content.match(/\{([^}]+)\}/g) || [];
        return matches.map(match => match.slice(1, -1));
    };

    // Handle template selection for variable insertion
    const handleChooseTemplate = (template) => {
        if (setTemplateName && typeof setTemplateName === 'function') {
            setTemplateName(template.template_name);
        }
        if (setTemplateContent && typeof setTemplateContent === 'function') {
            setTemplateContent(template.content);
        }
        if (setTemplateSystemPrompt && typeof setTemplateSystemPrompt === 'function') {
            setTemplateSystemPrompt(template.system_prompt || '');
        }
        if (templateID !== undefined && setTemplateID && typeof setTemplateID === 'function') {
            setTemplateID(template.template_id);
        }
        // Fire template selection handler if provided
        if (handleTemplateSelection && typeof handleTemplateSelection === 'function') {
            handleTemplateSelection(template);
        }
        showSnackbar(`Template "${template.template_name}" selected`, 'success');
    };

    // Function to open the Edit Dialog for template editing
    const openEditDialog = (template) => {
        setEditingTemplate({
            template_id: template.template_id,
            template_name: template.template_name,
            content: template.content,
            system_prompt: template.system_prompt || '',
            template_type: template.template_type,
            variables: extractVariablesFromContent(template.content)
        });
        setEditDialogOpen(true);
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <IconButton onClick={handleNavigateToHome} sx={{ mr: 1 }}>
                        <ArrowBackIcon />
                    </IconButton>
                    <Typography variant="h5" component="h1" gutterBottom sx={{ flexGrow: 1 }}>
                        Template Management
                    </Typography>
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => fetchTemplatesInternal()}
                        startIcon={<RefreshIcon />}
                        sx={{ mr: 2 }}
                    >
                        Refresh Templates
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleCreateNewTemplate}
                        startIcon={<AddIcon />}
                    >
                        Create Template
                    </Button>
                </Box>
                
                <Divider sx={{ mb: 3 }} />
                
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
                                    helperText="Required for managing templates"
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
                            <Grid item xs={12} md={9}>
                                <TextField
                                    fullWidth
                                    label="Agent ID"
                                    value={agentId}
                                    onChange={(e) => setAgentId(e.target.value)}
                                    placeholder="Enter an agent ID"
                                    helperText="Required for managing templates"
                                    required
                                />
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <Button 
                                    variant="contained" 
                                    color="primary"
                                    onClick={() => {
                                        if (agentId) {
                                            // Save to localStorage
                                            localStorage.setItem('agentId', agentId);
                                            setShowAgentIdInput(false);
                                            showSnackbar('Agent ID saved', 'success');
                                            // Fetch templates for this agent
                                            fetchTemplatesInternal();
                                        } else {
                                            showSnackbar('Please enter an Agent ID', 'error');
                                        }
                                    }}
                                    fullWidth
                                    sx={{ height: '56px' }}
                                >
                                    Save & Use
                                </Button>
                            </Grid>
                            <Grid item xs={12} mt={2}>
                                <Typography variant="body2" color="text.secondary">
                                    After saving or changing the agent ID, click the button below to load templates:
                                </Typography>
                                <Button 
                                    variant="outlined" 
                                    fullWidth
                                    onClick={fetchTemplatesInternal}
                                    startIcon={<RefreshIcon />}
                                    sx={{ mt: 1 }}
                                >
                                    Load Templates for this Agent
                                </Button>
                            </Grid>
                        </Grid>
                    </Box>
                )}
                
                {/* Template filter */}
                <Box sx={{ mb: 3 }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                label="Search Templates"
                                value={filterType}
                                onChange={(e) => setFilterType(e.target.value)}
                                placeholder="Search by type"
                            />
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <FormControl fullWidth>
                                <InputLabel id="filter-type-label">Filter by Type</InputLabel>
                                <Select
                                    labelId="filter-type-label"
                                    value={filterType}
                                    onChange={(e) => setFilterType(e.target.value)}
                                    label="Filter by Type"
                                >
                                    <MenuItem value="all">All Templates</MenuItem>
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
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Button
                                variant="outlined"
                                startIcon={<RefreshIcon />}
                                onClick={() => {
                                    // Use the internal implementation if fetchTemplates is not a function
                                    if (typeof fetchTemplates === 'function') {
                                        fetchTemplates();
                                    } else {
                                        fetchTemplatesInternal();
                                    }
                                }}
                            >
                                Refresh
                            </Button>
                        </Grid>
                    </Grid>
                </Box>
                
                {isLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        {filteredTemplates.length === 0 ? (
                            <Alert severity="info">
                                No templates found. Create your first template to get started.
                            </Alert>
                        ) : (
                            <List sx={{ bgcolor: 'background.paper' }}>
                                {filteredTemplates.map((template) => (
                                    <ListItem
                                        key={template.template_id}
                                        button
                                        onClick={() => handleEditExistingTemplate(template.template_id)}
                                        sx={{ 
                                            mb: 1,
                                            borderLeft: isDefaultTemplate(template.template_type) ? '4px solid #f50057' : 'none',
                                            bgcolor: isDefaultTemplate(template.template_type) ? 'rgba(245, 0, 87, 0.04)' : 'background.paper'
                                        }}
                                    >
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                    {isDefaultTemplate(template.template_type) && (
                                                        <Tooltip title="Default Template">
                                                            <StarIcon sx={{ mr: 1, color: 'secondary.main', fontSize: '1rem' }} />
                                                        </Tooltip>
                                                    )}
                                                    <Typography variant="subtitle1">
                                                        {template.template_name || 'Unnamed Template'}
                                                    </Typography>
                                                    <Chip 
                                                        size="small" 
                                                        label={getTemplateTypeLabel(template.template_type)} 
                                                        sx={{ ml: 1 }}
                                                        color={isDefaultTemplate(template.template_type) ? 'secondary' : 'primary'}
                                                        variant={isDefaultTemplate(template.template_type) ? 'filled' : 'outlined'}
                                                    />
                                                </Box>
                                            }
                                            secondary={
                                                <>
                                                    <Typography component="span" variant="body2" color="text.secondary">
                                                        {template.template_description || 'No description'}
                                                    </Typography>
                                                    <Typography component="span" variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                                        ID: {template.template_id}
                                                    </Typography>
                                                </>
                                            }
                                        />
                                        <ListItemSecondaryAction>
                                            <Tooltip title="Edit Template">
                                                <IconButton 
                                                    edge="end" 
                                                    aria-label="edit"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleEditExistingTemplate(template.template_id);
                                                    }}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Duplicate Template">
                                                <IconButton 
                                                    edge="end" 
                                                    aria-label="duplicate"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDuplicateTemplate(template);
                                                    }}
                                                >
                                                    <ContentCopyIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Delete Template">
                                                <IconButton 
                                                    edge="end" 
                                                    aria-label="delete"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteTemplate(template.template_id);
                                                    }}
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                ))}
                            </List>
                        )}
                    </>
                )}
                
                {/* Edit Template Dialog */}
                <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
                    <DialogTitle>Edit Template: {editingTemplate.template_name}</DialogTitle>
                    <DialogContent>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <TextField
                                    label="Template Name" 
                                    value={editingTemplate.template_name}
                                    onChange={(e) => setEditingTemplate({...editingTemplate, template_name: e.target.value})}
                                    fullWidth
                                    margin="normal"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <FormControl fullWidth margin="normal">
                                    <InputLabel>Template Type</InputLabel>
                                    <Select
                                        value={editingTemplate.template_type}
                                        onChange={(e) => setEditingTemplate({...editingTemplate, template_type: e.target.value})}
                                        label="Template Type"
                                    >
                                        {templateTypes.map((type) => (
                                            <MenuItem key={type.value} value={type.value}>
                                                {type.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="Template Content"
                                    value={editingTemplate.content}
                                    onChange={(e) => setEditingTemplate({...editingTemplate, content: e.target.value})}
                                    fullWidth
                                    multiline
                                    rows={6}
                                    margin="normal"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="System Prompt (Optional)"
                                    value={editingTemplate.system_prompt}
                                    onChange={(e) => setEditingTemplate({...editingTemplate, system_prompt: e.target.value})}
                                    fullWidth
                                    multiline
                                    rows={3}
                                    margin="normal"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <Box sx={{ mt: 1 }}>
                                    <Typography variant="subtitle2">Variables detected:</Typography>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                                        {editingTemplate.variables.map((variable, idx) => (
                                            <Chip key={idx} label={variable} size="small" />
                                        ))}
                                        {editingTemplate.variables.length === 0 && (
                                            <Typography variant="body2" color="text.secondary">
                                                No variables detected. Use {'{variable_name}'} syntax to create variables.
                                            </Typography>
                                        )}
                                    </Box>
                                </Box>
                            </Grid>
                        </Grid>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
                        <Button 
                            onClick={handleUpdateTemplate}
                            color="primary" 
                            variant="contained"
                            disabled={!editingTemplate.template_name || !editingTemplate.content}
                        >
                            Save Changes
                        </Button>
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
        </Container>
    );
}

export default TemplateManagement;