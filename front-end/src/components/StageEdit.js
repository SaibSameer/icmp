import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert, FormControl, InputLabel, Select, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { API_CONFIG } from '../config';

function StageEdit() {
    const { businessId, stageId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const query = new URLSearchParams(location.search);
    const agentId = query.get('agent_id');

    const [stage, setStage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [templates, setTemplates] = useState({
        selection: null,
        extraction: null,
        generation: null
    });
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const [formData, setFormData] = useState({
        stage_name: '',
        stage_description: '',
        stage_type: '',
        stage_selection_template_id: '',
        data_extraction_template_id: '',
        response_generation_template_id: ''
    });

    const adminApiKey = sessionStorage.getItem('adminApiKey');

    useEffect(() => {
        const fetchStage = async () => {
            if (!businessId || !stageId || !agentId || !adminApiKey) {
                setError('Missing required parameters');
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/api/stages/${stageId}?business_id=${businessId}&agent_id=${agentId}`, {
                    headers: {
                        'Authorization': `Bearer ${adminApiKey}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error ${response.status}`);
                }

                const data = await response.json();
                setStage(data);
                setFormData({
                    stage_name: data.stage_name || '',
                    stage_description: data.stage_description || '',
                    stage_type: data.stage_type || '',
                    stage_selection_template_id: data.stage_selection_template_id || '',
                    data_extraction_template_id: data.data_extraction_template_id || '',
                    response_generation_template_id: data.response_generation_template_id || ''
                });

                // Fetch template details for each template ID
                await Promise.all([
                    fetchTemplateDetails(data.stage_selection_template_id, 'selection'),
                    fetchTemplateDetails(data.data_extraction_template_id, 'extraction'),
                    fetchTemplateDetails(data.response_generation_template_id, 'generation')
                ]);
            } catch (err) {
                console.error('Error fetching stage:', err);
                setError(`Failed to fetch stage: ${err.message}`);
            } finally {
                setLoading(false);
            }
        };

        fetchStage();
    }, [businessId, stageId, agentId, adminApiKey]);

    const fetchTemplateDetails = async (templateId, type) => {
        if (!templateId) return;

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/templates/${templateId}?business_id=${businessId}`, {
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }

            const data = await response.json();
            setTemplates(prev => ({
                ...prev,
                [type]: data
            }));
        } catch (err) {
            console.error(`Error fetching ${type} template details:`, err);
        }
    };

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setSaving(true);
        setError(null);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/stages/${stageId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    ...formData,
                    business_id: businessId,
                    agent_id: agentId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            navigate(`/business/${businessId}/stages?agent_id=${agentId}`);
        } catch (err) {
            console.error('Error updating stage:', err);
            setError(`Failed to update stage: ${err.message}`);
        } finally {
            setSaving(false);
        }
    };

    const handleEditTemplate = (templateId) => {
        if (templateId) {
            navigate(`/business/${businessId}/templates/${templateId}/edit?agent_id=${agentId}`);
        }
    };

    const handleDelete = () => {
        setDeleteDialogOpen(true);
    };

    const handleConfirmDelete = async () => {
        setIsDeleting(true);
        setError(null);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/stages/${stageId}?business_id=${businessId}&agent_id=${agentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Failed to delete stage');
            }

            // Navigate back to stages list after successful deletion
            navigate(`/business/${businessId}/stages?agent_id=${agentId}`);
        } catch (err) {
            console.error('Error deleting stage:', err);
            setError(`Failed to delete stage: ${err.message}`);
        } finally {
            setIsDeleting(false);
            setDeleteDialogOpen(false);
        }
    };

    const handleCloseDeleteDialog = () => {
        setDeleteDialogOpen(false);
    };

    const renderTemplateSection = (type, templateId) => {
        const template = templates[type];
        const title = type.charAt(0).toUpperCase() + type.slice(1);
        
        return (
            <Box sx={{ mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6">{title} Template</Typography>
                    <Button
                        variant="outlined"
                        startIcon={<EditIcon />}
                        onClick={() => handleEditTemplate(templateId)}
                        disabled={!templateId}
                    >
                        Edit Template
                    </Button>
                </Box>
                {template ? (
                    <Box>
                        <Typography variant="subtitle1">{template.template_name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                            ID: {template.template_id}
                        </Typography>
                    </Box>
                ) : (
                    <Typography color="text.secondary">No template selected</Typography>
                )}
            </Box>
        );
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (!stage) {
        return <Alert severity="error">Stage not found</Alert>;
    }

    return (
        <Box sx={{ mt: 2 }}>
            <Button 
                onClick={() => navigate(`/business/${businessId}/stages?agent_id=${agentId}`)} 
                sx={{ mb: 2 }}
            >
                Back to Stages
            </Button>

            <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5">
                        Edit Stage
                    </Typography>
                    <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={handleDelete}
                        disabled={isDeleting}
                    >
                        {isDeleting ? 'Deleting...' : 'Delete Stage'}
                    </Button>
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                <form onSubmit={handleSubmit}>
                    <TextField
                        fullWidth
                        label="Stage Name"
                        name="stage_name"
                        value={formData.stage_name}
                        onChange={handleInputChange}
                        margin="normal"
                        required
                    />

                    <TextField
                        fullWidth
                        label="Stage Description"
                        name="stage_description"
                        value={formData.stage_description}
                        onChange={handleInputChange}
                        margin="normal"
                        multiline
                        rows={3}
                    />

                    <FormControl fullWidth margin="normal">
                        <InputLabel>Stage Type</InputLabel>
                        <Select
                            name="stage_type"
                            value={formData.stage_type}
                            onChange={handleInputChange}
                            required
                        >
                            <MenuItem value="conversation">Conversation</MenuItem>
                            <MenuItem value="routing">Routing</MenuItem>
                            <MenuItem value="tool_use">Tool Use</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Template sections with edit buttons */}
                    {renderTemplateSection('selection', formData.stage_selection_template_id)}
                    {renderTemplateSection('extraction', formData.data_extraction_template_id)}
                    {renderTemplateSection('generation', formData.response_generation_template_id)}

                    <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={saving}
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={() => navigate(`/business/${businessId}/stages?agent_id=${agentId}`)}
                            disabled={saving}
                        >
                            Cancel
                        </Button>
                    </Box>
                </form>
            </Paper>

            <Dialog
                open={deleteDialogOpen}
                onClose={handleCloseDeleteDialog}
            >
                <DialogTitle>Confirm Delete</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete the stage "{stage?.stage_name}"? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDeleteDialog} color="primary">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleConfirmDelete}
                        color="error"
                        variant="contained"
                        disabled={isDeleting}
                    >
                        {isDeleting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default StageEdit;