import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Box, Typography, List, ListItem, ListItemButton, ListItemText, CircularProgress, Alert, Button, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, FormControl, InputLabel, Checkbox, FormControlLabel, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import { API_CONFIG } from '../config';

function StagesList() {
    console.log('--- StagesList Component Mounting --- ');
    const { businessId } = useParams();
    const location = useLocation();
    const query = new URLSearchParams(location.search);
    const agentId = query.get('agent_id');
    const navigate = useNavigate();

    const [stages, setStages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [openAddStageDialog, setOpenAddStageDialog] = useState(false);
    const [newStageName, setNewStageName] = useState('');
    const [newStageDescription, setNewStageDescription] = useState('');
    const [newStageType, setNewStageType] = useState('conversation');
    const [selectedSelTemplate, setSelectedSelTemplate] = useState('');
    const [selectedExtTemplate, setSelectedExtTemplate] = useState('');
    const [selectedGenTemplate, setSelectedGenTemplate] = useState('');
    const [availableTemplates, setAvailableTemplates] = useState([]);
    const [loadingTemplates, setLoadingTemplates] = useState(false);
    const [errorTemplates, setErrorTemplates] = useState(null);
    const [addingStage, setAddingStage] = useState(false);
    const [addStageError, setAddStageError] = useState(null);

    const adminApiKey = sessionStorage.getItem('adminApiKey');

    useEffect(() => {
        if (!agentId) {
            setError('Agent ID is required for this view.');
            setLoading(false);
            return;
        }
        if (!businessId) {
            setError('Business ID is required for this view.');
            setLoading(false);
            return;
        }
        if (!adminApiKey) {
            setError('Admin API Key not found. Please configure it.');
            setLoading(false);
            return;
        }

        const fetchStages = async () => {
            console.log('[StagesList useEffect] Running fetchStages. businessId:', businessId, 'agentId:', agentId);
            setLoading(true);
            setError(null);

            try {
                const apiUrl = `${API_CONFIG.BASE_URL}/api/stages?business_id=${businessId}&agent_id=${agentId}`;
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${adminApiKey}`,
                        'Accept': 'application/json',
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error ${response.status}`);
                }

                const data = await response.json();
                setStages(data || []);
            } catch (err) {
                console.error("Failed to fetch stages:", err);
                setError(`Failed to fetch stages: ${err.message}`);
                setStages([]);
            } finally {
                setLoading(false);
            }
        };

        fetchStages();
    }, [businessId, agentId, adminApiKey]);

    const fetchAvailableTemplates = async () => {
        if (!businessId || !adminApiKey) {
            setErrorTemplates("Cannot fetch templates without Business ID and Admin Key.");
            return;
        }
        setLoadingTemplates(true);
        setErrorTemplates(null);
        setAddStageError(null);
        try {
             // Fetch ALL templates for the specific business
             const apiUrl = `${API_CONFIG.BASE_URL}/api/templates?business_id=${businessId}`;
             console.log("Fetching ALL templates from:", apiUrl);
             const response = await fetch(apiUrl, {
                 method: 'GET',
                 headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json',
                },
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }
            const data = await response.json();
            console.log("Fetched all templates:", data);
            setAvailableTemplates(data || []); // Store all fetched templates

            // Find the default template for each type using the is_default flag
            const defaultSel = data.find(t => t.template_type === 'selection' && t.is_default);
            const defaultExt = data.find(t => t.template_type === 'extraction' && t.is_default);
            const defaultGen = data.find(t => t.template_type === 'generation' && t.is_default);
            
            // Pre-select the defaults if found
            setSelectedSelTemplate(defaultSel ? defaultSel.template_id : '');
            setSelectedExtTemplate(defaultExt ? defaultExt.template_id : '');
            setSelectedGenTemplate(defaultGen ? defaultGen.template_id : '');

        } catch (err) {
            console.error("Failed to fetch all templates:", err);
            setErrorTemplates(`Failed to fetch templates: ${err.message}`);
            setAvailableTemplates([]);
        } finally {
            setLoadingTemplates(false);
        }
    };

    const handleOpenAddStageDialog = () => {
        setNewStageName('');
        setNewStageDescription('');
        setNewStageType('conversation');
        setSelectedSelTemplate('');
        setSelectedExtTemplate('');
        setSelectedGenTemplate('');
        setAddStageError(null);
        // Fetch all templates, which will also set the defaults
        fetchAvailableTemplates().then(() => {
             setOpenAddStageDialog(true);
        });
    };

    const handleCloseAddStageDialog = () => {
        setOpenAddStageDialog(false);
    };

    const handleAddStage = async () => {
        setAddingStage(true);
        setAddStageError(null);

        // Validation
        if (!newStageName.trim()) {
             setAddStageError("Stage Name is required.");
             setAddingStage(false);
             return;
        }
        if (!selectedSelTemplate || !selectedExtTemplate || !selectedGenTemplate) {
            setAddStageError("All three Template selections (Selection, Extraction, Generation) are required. Ensure default templates exist for this business.");
            setAddingStage(false);
            return;
        }
        if (!businessId || !agentId) {
             setAddStageError("Business ID and Agent ID are missing. Cannot create stage.");
             setAddingStage(false);
             return;
        }

        const payload = {
            business_id: businessId,
            agent_id: agentId, // Agent ID is crucial here
            stage_name: newStageName.trim(),
            stage_description: newStageDescription.trim() || null, // Send null if empty
            stage_type: newStageType,
            stage_selection_template_id: selectedSelTemplate,
            data_extraction_template_id: selectedExtTemplate,
            response_generation_template_id: selectedGenTemplate,
        };

        console.log("Creating stage with payload:", payload);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/stages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }
            
            handleCloseAddStageDialog();
            // Ideally, refresh the stage list here instead of alert
            // For now, alert and require manual refresh
            alert('Stage created successfully! Please refresh the page or navigate back and forth to see the new stage.');
            // TODO: Implement automatic refresh of the stages list

        } catch (err) {
            console.error("Failed to add stage:", err);
            setAddStageError(`Failed to add stage: ${err.message}`);
        } finally {
            setAddingStage(false);
        }
    };

    const filterTemplates = (type) => {
        return availableTemplates.filter(t => t.template_type === type);
    };

    const handleEditStage = (stageId, event) => {
        // Prevent the ListItemButton click from triggering
        event.stopPropagation();
        // Navigate to the edit page
        navigate(`/business/${businessId}/stages/${stageId}/edit${agentId ? `?agent_id=${agentId}` : ''}`);
    };

    console.log('[StagesList Render] Component rendering. businessId:', businessId, 'agentId:', agentId);

    if (!businessId) {
        return <Alert severity="error">Missing Business ID in URL.</Alert>;
    }
    if (!agentId) {
        return <Alert severity="error">Missing Agent ID in URL query parameter.</Alert>;
    }
    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    console.log('[StagesList Render] Proceeding to render main content. Error state:', error, 'Stages count:', stages.length);

    return (
        <Box sx={{ mt: 2 }}>
            <Button onClick={() => navigate(`/business/${businessId}`)} sx={{ mb: 2 }}>
                Back to Business Details
            </Button>
            <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h5">
                        Stages for Agent {agentId}
                    </Typography>
                    <Box>
                        <Button 
                            variant="outlined" 
                            startIcon={<AddIcon />} 
                            onClick={handleOpenAddStageDialog}
                            disabled={!businessId || !agentId || loadingTemplates} 
                            sx={{ mr: 1 }}
                        >
                            Add Stage
                        </Button>
                        <Button 
                            variant="outlined"
                            startIcon={<AddIcon />}
                            onClick={() => navigate(`/business/${businessId}/templates/new${agentId ? `?agent_id=${agentId}` : ''}`)}
                            disabled={!businessId || loadingTemplates}
                        >
                            Create Template
                        </Button>
                    </Box>
                </Box>
                <Typography variant="subtitle1" gutterBottom sx={{ mb: 2 }}>
                     (Business: {businessId})
                </Typography>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                {!loading && !error && stages.length === 0 ? (
                    <Typography>No stages found for this agent.</Typography>
                ) : (
                    <List component="nav" aria-label="stages list">
                        {stages.map((stage) => (
                            <ListItem 
                                key={stage.stage_id} 
                                disablePadding
                                secondaryAction={
                                    <IconButton 
                                        edge="end" 
                                        aria-label="edit"
                                        onClick={(e) => handleEditStage(stage.stage_id, e)}
                                    >
                                        <EditIcon />
                                    </IconButton>
                                }
                            >
                                <ListItemButton>
                                    <ListItemText
                                        primary={stage.stage_name}
                                        secondary={
                                            <React.Fragment>
                                                <Typography component="span" variant="body2" color="text.primary">
                                                    {stage.stage_description}
                                                </Typography>
                                                <br />
                                                <Typography component="span" variant="body2" color="text.secondary">
                                                    Type: {stage.stage_type} | Created: {new Date(stage.created_at).toLocaleDateString()}
                                                </Typography>
                                            </React.Fragment>
                                        }
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                )}
            </Paper>

            <Dialog open={openAddStageDialog} onClose={handleCloseAddStageDialog} maxWidth="md" fullWidth>
                <DialogTitle>Add New Stage for Agent {agentId}</DialogTitle>
                <DialogContent>
                     {/* Loading/Error for template fetch */}
                     {loadingTemplates && <CircularProgress sx={{ display: 'block', margin: 'auto', mb: 2 }} />}
                     {errorTemplates && <Alert severity="error" sx={{ mb: 2 }}>{errorTemplates}</Alert>}
                     
                     {/* Error during stage add */}
                    {addStageError && <Alert severity="error" sx={{ mb: 2 }}>{addStageError}</Alert>}
                    
                    {/* Form Fields */}
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Stage Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={newStageName}
                        onChange={(e) => setNewStageName(e.target.value)}
                        required
                        sx={{ mb: 2 }}
                        disabled={loadingTemplates || addingStage}
                    />
                    <TextField
                        margin="dense"
                        label="Stage Description (Optional)"
                        type="text"
                        fullWidth
                        variant="outlined"
                        multiline
                        rows={3}
                        value={newStageDescription}
                        onChange={(e) => setNewStageDescription(e.target.value)}
                        sx={{ mb: 2 }}
                        disabled={loadingTemplates || addingStage}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }} disabled={loadingTemplates || addingStage}>
                        <InputLabel>Stage Type</InputLabel>
                        <Select
                            value={newStageType}
                            label="Stage Type"
                            onChange={(e) => setNewStageType(e.target.value)}
                        >
                            {/* Add other types if needed based on backend */}
                            <MenuItem value="conversation">Conversation</MenuItem>
                            <MenuItem value="routing">Routing</MenuItem>
                            <MenuItem value="tool_use">Tool Use</MenuItem> 
                        </Select>
                    </FormControl>

                    <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Assign Templates</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Default templates are pre-selected if available. You can choose others.
                    </Typography>
                     
                    {/* Template Select Dropdowns (Modified to show all, indicate defaults) */}
                    <FormControl fullWidth sx={{ mb: 2 }} required error={!selectedSelTemplate && !!addStageError} disabled={loadingTemplates || addingStage || !!errorTemplates}>
                        <InputLabel>Selection Template</InputLabel>
                        <Select
                            value={selectedSelTemplate}
                            label="Selection Template"
                            onChange={(e) => setSelectedSelTemplate(e.target.value)}
                        >
                            <MenuItem value=""><em>Select a template</em></MenuItem>
                            {filterTemplates('selection').map(t => (
                                <MenuItem key={t.template_id} value={t.template_id}>
                                    {t.template_name} {t.is_default ? ' (Default)' : ''} 
                                    <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                                        ID: {t.template_id.substring(0, 8)}...
                                    </Typography>
                                </MenuItem>
                            ))}
                        </Select>
                        {filterTemplates('selection').length === 0 && !loadingTemplates && <Typography variant="caption" color="text.secondary" sx={{mt: 1}}>No selection templates found for this business.</Typography>}
                    </FormControl>

                    <FormControl fullWidth sx={{ mb: 2 }} required error={!selectedExtTemplate && !!addStageError} disabled={loadingTemplates || addingStage || !!errorTemplates}>
                        <InputLabel>Extraction Template</InputLabel>
                        <Select
                            value={selectedExtTemplate}
                            label="Extraction Template"
                            onChange={(e) => setSelectedExtTemplate(e.target.value)}
                        >
                             <MenuItem value=""><em>Select a template</em></MenuItem>
                             {filterTemplates('extraction').map(t => (
                                <MenuItem key={t.template_id} value={t.template_id}>
                                    {t.template_name} {t.is_default ? ' (Default)' : ''}
                                     <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                                        ID: {t.template_id.substring(0, 8)}...
                                    </Typography>
                                </MenuItem>
                            ))}
                        </Select>
                         {filterTemplates('extraction').length === 0 && !loadingTemplates && <Typography variant="caption" color="text.secondary" sx={{mt: 1}}>No extraction templates found for this business.</Typography>}
                   </FormControl>

                     <FormControl fullWidth sx={{ mb: 2 }} required error={!selectedGenTemplate && !!addStageError} disabled={loadingTemplates || addingStage || !!errorTemplates}>
                        <InputLabel>Generation Template</InputLabel>
                        <Select
                            value={selectedGenTemplate}
                            label="Generation Template"
                            onChange={(e) => setSelectedGenTemplate(e.target.value)}
                        >
                             <MenuItem value=""><em>Select a template</em></MenuItem>
                            {filterTemplates('generation').map(t => (
                                <MenuItem key={t.template_id} value={t.template_id}>
                                    {t.template_name} {t.is_default ? ' (Default)' : ''}
                                     <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                                        ID: {t.template_id.substring(0, 8)}...
                                    </Typography>
                                </MenuItem>
                            ))}
                        </Select>
                         {filterTemplates('generation').length === 0 && !loadingTemplates && <Typography variant="caption" color="text.secondary" sx={{mt: 1}}>No generation templates found for this business.</Typography>}
                    </FormControl>

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseAddStageDialog} disabled={addingStage}>Cancel</Button>
                    <Button 
                        onClick={handleAddStage} 
                        variant="contained" 
                        // More specific disabling logic
                        disabled={addingStage || loadingTemplates || !!errorTemplates || !newStageName.trim() || !selectedSelTemplate || !selectedExtTemplate || !selectedGenTemplate}
                    >
                        {addingStage ? <CircularProgress size={24} /> : "Add Stage"}
                    </Button>
                </DialogActions>
            </Dialog>

        </Box>
    );
}

export default StagesList;