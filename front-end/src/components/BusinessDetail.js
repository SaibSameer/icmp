import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert, TextField, Button, Paper, Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, ListItemButton } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import MessageIcon from '@mui/icons-material/Message';
import { API_CONFIG } from '../config';
import AgentSection from './AgentSection';

function BusinessDetail() {
    const { businessId } = useParams();
    const navigate = useNavigate();
    
    // Business Data State
    const [businessData, setBusinessData] = useState(null);
    const [editableData, setEditableData] = useState({});
    const [loadingBusiness, setLoadingBusiness] = useState(true);
    const [errorBusiness, setErrorBusiness] = useState(null);
    const [updateSuccess, setUpdateSuccess] = useState(null);
    const [updateError, setUpdateError] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [defaultStages, setDefaultStages] = useState([]);
    const [loadingDefaultStages, setLoadingDefaultStages] = useState(true);
    const [errorDefaultStages, setErrorDefaultStages] = useState(null);

    const adminApiKey = sessionStorage.getItem('adminApiKey');

    // --- Fetch Business Details --- 
    const fetchBusinessDetails = useCallback(async () => {
        setLoadingBusiness(true);
        setErrorBusiness(null);
        setUpdateSuccess(null);
        setUpdateError(null);

        if (!adminApiKey) {
            setErrorBusiness('Admin API Key not found.');
            setLoadingBusiness(false);
            return;
        }
        if (!businessId) {
             setErrorBusiness('Business ID not found in URL.');
             setLoadingBusiness(false);
             return;
        }

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/${businessId}`, {
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
            setBusinessData(data);
            setEditableData({ 
                business_name: data.business_name || '',
                business_description: data.business_description || '',
                address: data.address || '',
                phone_number: data.phone_number || '',
                website: data.website || '',
                owner_id: data.owner_id || '',
                first_stage_id: data.first_stage_id || '' 
            });
            setIsEditing(false);
        } catch (err) {
            console.error("Failed to fetch business details:", err);
            setErrorBusiness(`Failed to fetch business details: ${err.message}`);
        } finally {
            setLoadingBusiness(false);
        }
    }, [businessId, adminApiKey]);

    // Add new function to fetch default stages
    const fetchDefaultStages = useCallback(async () => {
        if (!adminApiKey || !businessId) return;
        
        setLoadingDefaultStages(true);
        setErrorDefaultStages(null);
        
        try {
            // No agent_id parameter means we'll get default stages
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/stages?business_id=${businessId}`, {
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
            setDefaultStages(data);
        } catch (err) {
            console.error("Failed to fetch default stages:", err);
            setErrorDefaultStages(`Failed to fetch default stages: ${err.message}`);
        } finally {
            setLoadingDefaultStages(false);
        }
    }, [businessId, adminApiKey]);

    useEffect(() => {
        fetchBusinessDetails();
        fetchDefaultStages();
    }, [fetchBusinessDetails, fetchDefaultStages]);

    // --- Edit Mode Handlers ---
    const handleEditClick = () => {
        setIsEditing(true);
        setUpdateSuccess(null);
        setUpdateError(null);
    };

    const handleCancelClick = () => {
        setEditableData({ 
            business_name: businessData.business_name || '',
            business_description: businessData.business_description || '',
            address: businessData.address || '',
            phone_number: businessData.phone_number || '',
            website: businessData.website || '',
            owner_id: businessData.owner_id || '',
            first_stage_id: businessData.first_stage_id || '' 
        });
        setIsEditing(false);
        setUpdateError(null);
    };

    // --- Handle Business Update --- 
    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setEditableData(prev => ({ ...prev, [name]: value }));
    };

    const handleUpdateBusiness = async () => {
        setUpdateSuccess(null);
        setUpdateError(null);
        if (!adminApiKey) {
             setUpdateError('Admin API Key not found.');
             return;
        }
        // Simple validation (add more as needed)
        if (!editableData.business_name?.trim()) {
            setUpdateError('Business Name cannot be empty.');
            return;
        }

        const payload = { ...editableData };
        // Ensure potentially null IDs are actually null, not empty strings
        if (!payload.owner_id) payload.owner_id = null;
        if (!payload.first_stage_id) payload.first_stage_id = null;

        try {
             const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/${businessId}`, {
                method: 'PUT',
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
            setUpdateSuccess("Business details updated successfully!");
            setIsEditing(false);
            fetchBusinessDetails();
        } catch (err) {
            console.error("Failed to update business:", err);
            setUpdateError(`Update failed: ${err.message}`);
        }
    };

    // --- Handle Business Delete ---
    const handleDeleteBusiness = async () => {
        setDeleting(true);
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/${businessId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            navigate('/');
        } catch (err) {
            console.error("Failed to delete business:", err);
            setUpdateError(`Delete failed: ${err.message}`);
        } finally {
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    };

    const handleSnackbarOpen = (message, severity) => {
        if (severity === 'success') {
            setUpdateSuccess(message);
        } else {
            setUpdateError(message);
        }
    };

    // Add function to handle editing default stage
    const handleEditDefaultStage = (stageId) => {
        navigate(`/business/${businessId}/default-stages/${stageId}/edit`);
    };

    if (loadingBusiness) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (errorBusiness) {
        return (
            <Alert severity="error" sx={{ mt: 2 }}>
                {errorBusiness}
            </Alert>
        );
    }

    return (
        <Box>
            {/* Business Details Card */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h5">Business Details</Typography>
                    <Box>
                        <Button
                            variant="outlined"
                            onClick={() => navigate(`/business/${businessId}/information`)}
                            sx={{ mr: 2 }}
                        >
                            View Business Information
                        </Button>
                        <Button
                            startIcon={<MessageIcon />}
                            onClick={() => navigate(`/business/${businessId}/messages`)}
                            sx={{ mr: 2 }}
                        >
                            Messages
                        </Button>
                        <Button
                            startIcon={<EditIcon />}
                            onClick={handleEditClick}
                            disabled={isEditing}
                        >
                            Edit
                        </Button>
                    </Box>
                </Box>

                {updateSuccess && <Alert severity="success" sx={{ mb: 2 }}>{updateSuccess}</Alert>}
                {updateError && <Alert severity="error" sx={{ mb: 2 }}>{updateError}</Alert>}

                <Box component="form" noValidate>
                    <TextField
                        fullWidth
                        label="Business Name"
                        name="business_name"
                        value={editableData.business_name || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="Description"
                        name="business_description"
                        value={editableData.business_description || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                        multiline
                        rows={3}
                    />
                    <TextField
                        fullWidth
                        label="Address"
                        name="address"
                        value={editableData.address || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Phone Number"
                        name="phone_number"
                        value={editableData.phone_number || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Website"
                        name="website"
                        value={editableData.website || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Owner ID"
                        name="owner_id"
                        value={editableData.owner_id || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="First Stage ID"
                        name="first_stage_id"
                        value={editableData.first_stage_id || ''}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        margin="normal"
                    />

                    {isEditing && (
                        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                            <Button
                                variant="contained"
                                onClick={handleUpdateBusiness}
                            >
                                Save Changes
                            </Button>
                            <Button
                                variant="outlined"
                                onClick={handleCancelClick}
                            >
                                Cancel
                            </Button>
                        </Box>
                    )}
                </Box>
            </Paper>

            {/* Default Stages Section */}
            <Paper sx={{ p: 3, mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Default Stages
                </Typography>

                {errorDefaultStages && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {errorDefaultStages}
                    </Alert>
                )}

                {loadingDefaultStages ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                        <CircularProgress />
                    </Box>
                ) : defaultStages.length > 0 ? (
                    <List>
                        {defaultStages.map((stage) => (
                            <ListItem
                                key={stage.stage_id}
                                secondaryAction={
                                    <Button
                                        startIcon={<EditIcon />}
                                        onClick={() => handleEditDefaultStage(stage.stage_id)}
                                    >
                                        Edit
                                    </Button>
                                }
                            >
                                <ListItemText
                                    primary={stage.stage_name}
                                    secondary={stage.stage_description || 'No description'}
                                />
                            </ListItem>
                        ))}
                    </List>
                ) : (
                    <Typography color="text.secondary">
                        No default stages found
                    </Typography>
                )}
            </Paper>

            {/* Agents Section */}
            <AgentSection handleSnackbarOpen={handleSnackbarOpen} />

            {/* Delete Confirmation Dialog */}
            <Dialog
                open={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
            >
                <DialogTitle>Delete Business</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete this business? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button 
                        onClick={() => setShowDeleteConfirm(false)} 
                        disabled={deleting}
                    >
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleDeleteBusiness} 
                        color="error" 
                        disabled={deleting}
                        autoFocus
                    >
                        {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default BusinessDetail;