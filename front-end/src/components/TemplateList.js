import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Typography,
    Box,
    CircularProgress,
    Alert,
    Chip,
    Tooltip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { API_CONFIG } from '../config';

function TemplateList({ businessId, handleSnackbarOpen }) {
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const adminApiKey = sessionStorage.getItem('adminApiKey');

    const fetchTemplates = async () => {
        if (!businessId) {
            setError('Business ID is required');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/templates?business_id=${businessId}`, {
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
            setTemplates(data);
            setError(null);
        } catch (err) {
            console.error('Error fetching templates:', err);
            setError(err.message);
            if (handleSnackbarOpen) {
                handleSnackbarOpen(`Error loading templates: ${err.message}`, 'error');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTemplates();
    }, [businessId]);

    const handleEdit = (templateId) => {
        navigate(`/business/${businessId}/templates/${templateId}/edit`);
    };

    const handleDelete = async (templateId) => {
        if (!window.confirm('Are you sure you want to delete this template?')) {
            return;
        }

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/templates/${templateId}?business_id=${businessId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            if (handleSnackbarOpen) {
                handleSnackbarOpen('Template deleted successfully', 'success');
            }
            fetchTemplates(); // Refresh the list
        } catch (err) {
            console.error('Error deleting template:', err);
            if (handleSnackbarOpen) {
                handleSnackbarOpen(`Error deleting template: ${err.message}`, 'error');
            }
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                <CircularProgress size={24} />
                <Typography sx={{ ml: 1 }} variant="body2">Loading templates...</Typography>
            </Box>
        );
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    if (templates.length === 0) {
        return (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', p: 2 }}>
                No templates found. Click "Create Template" to add one.
            </Typography>
        );
    }

    return (
        <List dense>
            {templates.map((template) => (
                <ListItem key={template.template_id}>
                    <ListItemText
                        primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {template.template_name}
                                {template.is_default && (
                                    <Chip
                                        label="Default"
                                        size="small"
                                        color="primary"
                                        variant="outlined"
                                    />
                                )}
                            </Box>
                        }
                        secondary={
                            <>
                                <Typography variant="caption" component="span" color="text.secondary">
                                    Type: {template.template_type}
                                </Typography>
                            </>
                        }
                    />
                    <ListItemSecondaryAction>
                        <Tooltip title="Edit Template">
                            <IconButton edge="end" onClick={() => handleEdit(template.template_id)} sx={{ mr: 1 }}>
                                <EditIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Template">
                            <IconButton edge="end" onClick={() => handleDelete(template.template_id)}>
                                <DeleteIcon />
                            </IconButton>
                        </Tooltip>
                    </ListItemSecondaryAction>
                </ListItem>
            ))}
        </List>
    );
}

export default TemplateList;