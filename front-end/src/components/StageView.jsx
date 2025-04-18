import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    Paper,
    Typography,
    Divider,
    CircularProgress,
    Alert,
    Grid,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import { API_CONFIG } from '../config';
import EditIcon from '@mui/icons-material/Edit';
import useAgents from '../hooks/useAgents';

const StageView = () => {
    const { stageId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stageData, setStageData] = useState(null);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [newStageName, setNewStageName] = useState('');
    const [newStageDescription, setNewStageDescription] = useState('');
    const [editLoading, setEditLoading] = useState(false);
    const [editError, setEditError] = useState(null);
    const [editType, setEditType] = useState(''); // 'name', 'description', or 'agent'
    const [selectedAgentId, setSelectedAgentId] = useState('');
    const [agents, setAgents] = useState([]);
    const [agentsLoading, setAgentsLoading] = useState(false);
    const [agentsError, setAgentsError] = useState(null);

    // Fetch agents
    useEffect(() => {
        const fetchAgents = async () => {
            setAgentsLoading(true);
            setAgentsError(null);
            
            try {
                const businessId = localStorage.getItem('businessId');
                const businessApiKey = localStorage.getItem('businessApiKey');

                if (!businessId || !businessApiKey) {
                    setAgentsError('Authentication required. Please log in.');
                    setAgentsLoading(false);
                    return;
                }

                const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AGENTS}?business_id=${businessId}`, {
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${businessApiKey}`
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP error ${response.status}`);
                }

                const data = await response.json();
                setAgents(data);
            } catch (err) {
                console.error('Error fetching agents:', err);
                setAgentsError(err.message);
            } finally {
                setAgentsLoading(false);
            }
        };

        fetchAgents();
    }, []);

    useEffect(() => {
        const fetchStageData = async () => {
            if (!stageId) {
                setLoading(false);
                return;
            }

            try {
                const businessId = localStorage.getItem('businessId');
                const businessApiKey = localStorage.getItem('businessApiKey');

                if (!businessId || !businessApiKey) {
                    setError('Authentication required. Please log in.');
                    setLoading(false);
                    return;
                }

                const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STAGES}/${stageId}?business_id=${businessId}`, {
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${businessApiKey}`
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP error ${response.status}`);
                }

                const data = await response.json();
                console.log('Stage data:', data);
                setStageData(data);
                setNewStageName(data.stage_name);
                setNewStageDescription(data.stage_description || '');
                setSelectedAgentId(data.agent_id || '');
            } catch (err) {
                console.error('Error fetching stage:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchStageData();
    }, [stageId]);

    const handleEditClick = (type) => {
        setEditType(type);
        setEditDialogOpen(true);
    };

    const handleEditClose = () => {
        setEditDialogOpen(false);
        setEditError(null);
    };

    const handleSaveEdit = async () => {
        if (editType === 'name' && !newStageName.trim()) {
            setEditError('Stage name cannot be empty');
            return;
        }

        if (editType === 'description' && !newStageDescription.trim()) {
            setEditError('Stage description cannot be empty');
            return;
        }

        setEditLoading(true);
        setEditError(null);

        try {
            const businessId = localStorage.getItem('businessId')?.trim();
            const businessApiKey = localStorage.getItem('businessApiKey');

            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STAGES}/${stageId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${businessApiKey}`
                },
                body: JSON.stringify({
                    business_id: businessId,
                    stage_name: editType === 'name' ? newStageName.trim() : stageData.stage_name,
                    stage_description: editType === 'description' ? newStageDescription.trim() : stageData.stage_description,
                    stage_type: stageData.stage_type,
                    stage_selection_template_id: stageData.stage_selection_template_id,
                    data_extraction_template_id: stageData.data_extraction_template_id,
                    response_generation_template_id: stageData.response_generation_template_id,
                    agent_id: editType === 'agent' ? selectedAgentId : stageData.agent_id
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            // Fetch the updated stage data
            const updatedResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STAGES}/${stageId}?business_id=${businessId}`, {
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${businessApiKey}`
                }
            });

            if (!updatedResponse.ok) {
                throw new Error('Failed to fetch updated stage data');
            }

            const updatedData = await updatedResponse.json();
            setStageData(updatedData);
            setEditDialogOpen(false);
        } catch (err) {
            console.error('Error updating stage:', err);
            setEditError(err.message);
        } finally {
            setEditLoading(false);
        }
    };

    const handleAgentChange = (event) => {
        setSelectedAgentId(event.target.value);
    };

    const TemplateField = ({ label, templateId }) => (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body1" component="span">
                <strong>{label}:</strong> {templateId || 'Not set'}
            </Typography>
        </Box>
    );

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ mt: 2 }}>
                {error}
            </Alert>
        );
    }

    if (!stageData) {
        return (
            <Alert severity="info" sx={{ mt: 2 }}>
                No stage data available
            </Alert>
        );
    }

    return (
        <Paper sx={{ p: 3, mt: 2 }}>
            {/* Basic Information Section */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                    Basic Information
                </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="subtitle2" color="primary">Name</Typography>
                            <Typography>{stageData.stage_name}</Typography>
                        </Box>
                        <Button
                            startIcon={<EditIcon />}
                            variant="outlined"
                            onClick={() => handleEditClick('name')}
                        >
                            Edit Stage Name
                        </Button>
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="subtitle2" color="primary">Description</Typography>
                            <Typography>{stageData.stage_description || 'No description'}</Typography>
                        </Box>
                        <Button
                            startIcon={<EditIcon />}
                            variant="outlined"
                            onClick={() => handleEditClick('description')}
                        >
                            Edit Description
                        </Button>
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="subtitle2" color="primary">Agent</Typography>
                            <Typography>
                                {stageData.agent_id 
                                    ? agents.find(a => a.agent_id === stageData.agent_id)?.agent_name || 'Unknown Agent' 
                                    : 'No agent assigned'}
                            </Typography>
                        </Box>
                        <Button
                            startIcon={<EditIcon />}
                            variant="outlined"
                            onClick={() => handleEditClick('agent')}
                        >
                            Assign Agent
                        </Button>
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Typography variant="subtitle2" color="primary">Type</Typography>
                    <Typography>{stageData.stage_type}</Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="primary">Stage ID</Typography>
                    <Typography component="code">{stageData.stage_id}</Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="primary">Business ID</Typography>
                    <Typography component="code">{stageData.business_id}</Typography>
                </Grid>

                {stageData.agent_id && (
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="primary">Agent ID</Typography>
                        <Typography component="code">{stageData.agent_id}</Typography>
                    </Grid>
                )}
            </Grid>

            {/* Template Configuration Section */}
            <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
                Template Configuration
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="subtitle2" color="primary">Stage Selection Template</Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <TemplateField 
                            label="Stage Selection Template"
                            templateId={stageData.stage_selection_template_id}
                        />
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={() => navigate(`/template-editor/${stageData.stage_selection_template_id}`)}
                        >
                            Edit Template
                        </Button>
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Typography variant="subtitle2" color="primary">Data Extraction Template</Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <TemplateField 
                            label="Data Extraction Template"
                            templateId={stageData.data_extraction_template_id}
                        />
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={() => navigate(`/template-editor/${stageData.data_extraction_template_id}`)}
                        >
                            Edit Template
                        </Button>
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Typography variant="subtitle2" color="primary">Response Generation Template</Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <TemplateField 
                            label="Response Generation Template"
                            templateId={stageData.response_generation_template_id}
                        />
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={() => navigate(`/template-editor/${stageData.response_generation_template_id}`)}
                        >
                            Edit Template
                        </Button>
                    </Box>
                </Grid>
            </Grid>

            {/* Creation Date */}
            {stageData.created_at && (
                <Box mt={4}>
                    <Divider />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                        Created: {new Date(stageData.created_at).toLocaleString()}
                    </Typography>
                </Box>
            )}

            {/* Edit Dialog */}
            <Dialog open={editDialogOpen} onClose={handleEditClose}>
                <DialogTitle>
                    {editType === 'name' ? 'Edit Stage Name' : 
                     editType === 'description' ? 'Edit Stage Description' : 
                     'Assign Agent'}
                </DialogTitle>
                <DialogContent>
                    {editType === 'name' ? (
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Stage Name"
                            type="text"
                            fullWidth
                            value={newStageName}
                            onChange={(e) => setNewStageName(e.target.value)}
                            error={!!editError}
                            helperText={editError}
                        />
                    ) : editType === 'description' ? (
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Stage Description"
                            type="text"
                            fullWidth
                            multiline
                            rows={4}
                            value={newStageDescription}
                            onChange={(e) => setNewStageDescription(e.target.value)}
                            error={!!editError}
                            helperText={editError}
                        />
                    ) : (
                        <FormControl fullWidth margin="dense">
                            <InputLabel id="agent-select-label">Select Agent</InputLabel>
                            <Select
                                labelId="agent-select-label"
                                id="agent-select"
                                value={selectedAgentId}
                                label="Select Agent"
                                onChange={handleAgentChange}
                            >
                                <MenuItem value="">
                                    <em>None</em>
                                </MenuItem>
                                {agents.map((agent) => (
                                    <MenuItem key={agent.agent_id} value={agent.agent_id}>
                                        {agent.agent_name}
                                    </MenuItem>
                                ))}
                            </Select>
                            {editError && (
                                <Typography color="error" variant="caption">
                                    {editError}
                                </Typography>
                            )}
                        </FormControl>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleEditClose}>Cancel</Button>
                    <Button 
                        onClick={handleSaveEdit} 
                        variant="contained" 
                        disabled={editLoading}
                    >
                        {editLoading ? <CircularProgress size={24} /> : 'Save'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
}

export default StageView;