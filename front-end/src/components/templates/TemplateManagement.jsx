import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
    Box,
    Typography,
    Button,
    Container,
    Paper,
    List,
    ListItem,
    ListItemText,
    IconButton,
    TextField,
    Grid,
    Divider,
    CircularProgress,
    Alert,
    Tooltip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Menu,
    MenuItem
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CodeIcon from '@mui/icons-material/Code';
import TemplateVariablesWindow from './TemplateVariablesWindow';
import templateService from '../../services/templateService';

function TemplateManagement() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const businessId = searchParams.get('businessId');
    const agentId = searchParams.get('agentId');

    // State management
    const [templates, setTemplates] = useState([]);
    const [filteredTemplates, setFilteredTemplates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [variablesWindowOpen, setVariablesWindowOpen] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [showBusinessIdInput, setShowBusinessIdInput] = useState(false);
    const [businessApiKey, setBusinessApiKey] = useState('');
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [editContent, setEditContent] = useState('');
    const [variablesAnchorEl, setVariablesAnchorEl] = useState(null);
    const [availableVariables, setAvailableVariables] = useState([]);
    const [isLoadingVariables, setIsLoadingVariables] = useState(false);
    const [apiError, setApiError] = useState(null);

    // Template types for filtering
    const templateTypes = [
        { value: 'stage_selection', label: 'Stage Selection', group: 'Regular' },
        { value: 'data_extraction', label: 'Data Extraction', group: 'Regular' },
        { value: 'response_generation', label: 'Response Generation', group: 'Regular' },
        { value: 'default_stage_selection', label: 'Default Stage Selection', group: 'Default' },
        { value: 'default_data_extraction', label: 'Default Data Extraction', group: 'Default' },
        { value: 'default_response_generation', label: 'Default Response Generation', group: 'Default' }
    ];

    useEffect(() => {
        const initializeData = async () => {
            if (businessId && agentId) {
                try {
                    await fetchTemplates();
                    if (businessApiKey) {
                        await fetchAvailableVariables();
                    }
                } catch (error) {
                    console.error("Error initializing data:", error);
                    setError('Failed to initialize data. Please try again.');
                }
            }
        };
        initializeData();
    }, [businessId, agentId, businessApiKey]);

    useEffect(() => {
        setFilteredTemplates(templates);
    }, [templates]);

    const fetchTemplates = async () => {
        setLoading(true);
        setError('');
        try {
            console.log("Fetching templates for business:", businessId, "agent:", agentId);
            const response = await templateService.getTemplates(businessId, agentId);
            console.log("Templates fetched:", response);
            setTemplates(response);
        } catch (err) {
            console.error("Failed to fetch templates:", err);
            setError('Failed to fetch templates. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const fetchAvailableVariables = async () => {
        if (!businessApiKey) {
            console.log("No API key available for fetching variables");
            return;
        }

        setIsLoadingVariables(true);
        setApiError(null);
        try {
            console.log("Fetching variables with API key:", businessApiKey.substring(0, 5) + "...");
            const response = await fetch('http://localhost:5000/api/template-variables/available/', {
                headers: {
                    'Authorization': `Bearer ${businessApiKey}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const variables = await response.json();
                console.log("Variables fetched successfully:", variables);
                setAvailableVariables(variables);
            } else {
                const errorData = await response.json().catch(() => ({}));
                console.error("Failed to fetch variables:", response.status, errorData);
                setApiError(`Failed to fetch variables: ${response.status}`);
            }
        } catch (err) {
            console.error("Failed to fetch variables:", err);
            setApiError('Failed to connect to the server');
        } finally {
            setIsLoadingVariables(false);
        }
    };

    const handleCreateNewTemplate = () => {
        navigate(`/business/${businessId}/templates/new`);
    };

    const handleEditTemplate = (template) => {
        navigate(`/business/${businessId}/templates/${template.template_id}`);
    };

    const handleSaveTemplate = async () => {
        try {
            console.log("Saving template:", selectedTemplate ? "edit" : "new");
            if (selectedTemplate) {
                await templateService.updateTemplate(selectedTemplate.template_id, {
                    ...selectedTemplate,
                    content: editContent
                });
            } else {
                await templateService.createTemplate({
                    business_id: businessId,
                    agent_id: agentId,
                    content: editContent,
                    template_type: 'response_generation'
                });
            }
            setEditDialogOpen(false);
            await fetchTemplates();
        } catch (err) {
            console.error("Failed to save template:", err);
            setError('Failed to save template. Please try again.');
        }
    };

    const handleNavigateToHome = () => {
        navigate('/');
    };

    const handleVariablesClick = (event) => {
        setVariablesAnchorEl(event.currentTarget);
    };

    const handleVariablesClose = () => {
        setVariablesAnchorEl(null);
    };

    const handleInsertVariable = (variable) => {
        const variableText = `{{${variable}}}`;
        setEditContent(prev => prev + variableText);
        handleVariablesClose();
    };

    const isDefaultTemplate = (type) => {
        return type.startsWith('default_');
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
                        onClick={fetchTemplates}
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

                {showBusinessIdInput && (
                    <Box sx={{ mb: 3, p: 2, border: '1px dashed', borderColor: 'warning.main', borderRadius: 1 }}>
                        <Typography variant="subtitle1" color="warning.main" gutterBottom>
                            Business Credentials Required
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={5}>
                                <TextField
                                    fullWidth
                                    label="Business ID"
                                    value={businessId || ''}
                                    disabled
                                    helperText="Required for managing templates"
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
                        </Grid>
                    </Box>
                )}

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}

                {loading ? (
                    <Box display="flex" justifyContent="center" p={3}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <List>
                        {filteredTemplates.map((template, index) => (
                            <React.Fragment key={template.template_id}>
                                {index > 0 && <Divider />}
                                <ListItem
                                    secondaryAction={
                                        <Box>
                                            <Tooltip title="Edit Template">
                                                <IconButton
                                                    edge="end"
                                                    onClick={() => handleEditTemplate(template)}
                                                    sx={{ mr: 1 }}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>
                                    }
                                >
                                    <ListItemText
                                        primary={
                                            <Typography variant="subtitle1">
                                                {template.template_name || 'Unnamed Template'}
                                            </Typography>
                                        }
                                        secondary={
                                            <Box>
                                                <Typography variant="body2" color="text.secondary">
                                                    Type: {template.template_type}
                                                </Typography>
                                                <Typography variant="body2" color="text.secondary">
                                                    Last Updated: {new Date(template.updated_at).toLocaleString()}
                                                </Typography>
                                            </Box>
                                        }
                                    />
                                </ListItem>
                            </React.Fragment>
                        ))}
                    </List>
                )}
            </Paper>
        </Container>
    );
}

export default TemplateManagement;
