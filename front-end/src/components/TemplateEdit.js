import React, { useState, useEffect } from 'react';
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
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    DialogContentText,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { API_CONFIG } from '../config';
import TemplateVariablesWindow from './TemplateVariablesWindow';

function capitalizeType(type) {
    if (!type) return '';
    const map = {
        selection: 'Selection',
        extraction: 'Extraction',
        response: 'Response'
    };
    return map[type.toLowerCase()] || type;
}

function TemplateEdit() {
    const { businessId, templateId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const query = new URLSearchParams(location.search);
    const agentId = query.get('agent_id');

    const [template, setTemplate] = useState({
        template_name: '',
        content: '',
        system_prompt: '',
        template_type: '',
        business_id: businessId
    });

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [error, setError] = useState(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [success, setSuccess] = useState(null);

    // Variables window state
    const [variablesWindowOpen, setVariablesWindowOpen] = useState(false);
    const [activeField, setActiveField] = useState(null); // 'system_prompt' or 'content'
    const [contentRef, setContentRef] = useState(null);
    const [systemPromptRef, setSystemPromptRef] = useState(null);

    const adminApiKey = sessionStorage.getItem('adminApiKey');

    useEffect(() => {
        const fetchTemplate = async () => {
            if (!businessId || !templateId || !adminApiKey) {
                setError('Missing required parameters');
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/api/templates/${templateId}?business_id=${businessId}`, {
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
                setTemplate({
                    template_name: data.template_name || '',
                    content: data.content || '',
                    system_prompt: data.system_prompt || '',
                    template_type: capitalizeType(data.template_type),
                    business_id: businessId
                });
            } catch (err) {
                console.error('Error fetching template:', err);
                setError(`Failed to fetch template: ${err.message}`);
            } finally {
                setLoading(false);
            }
        };

        fetchTemplate();
    }, [businessId, templateId, adminApiKey]);

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setTemplate(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Map template types to their backend equivalents
            const templateTypeMap = {
                'selection': 'selection',
                'extraction': 'extraction',
                'response': 'generation'  // Map 'response' to 'generation'
            };

            // Ensure template_type is lowercase and mapped correctly
            const templateData = {
                ...template,
                template_type: templateTypeMap[template.template_type.toLowerCase()] || template.template_type.toLowerCase(),
                business_id: businessId
            };

            const response = await fetch(`${API_CONFIG.BASE_URL}/api/templates/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json',
                },
                body: JSON.stringify(templateData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            // Show success message and close the form
            setSuccess('Template updated successfully!');
            setTimeout(() => {
                navigate(`/business/${businessId}/templates`);
            }, 1500);

        } catch (err) {
            console.error('Error updating template:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        setDeleting(true);
        setError(null);

        try {
            const url = `${API_CONFIG.BASE_URL}/api/templates/${templateId}?business_id=${businessId}`;
            console.log('Attempting to delete template:', {
                url,
                templateId,
                businessId,
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json'
                }
            });

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${adminApiKey}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Delete template error response:', errorData);
                throw new Error(errorData.message || `HTTP error ${response.status}`);
            }

            console.log('Template deleted successfully');
            // Navigate back to stages list after successful deletion
            navigate(`/business/${businessId}/stages?agent_id=${agentId}`);
        } catch (err) {
            console.error('Error deleting template:', err);
            setError(`Failed to delete template: ${err.message}`);
        } finally {
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    };

    // Insert variable at cursor position in the correct field
    const handleVariableSelect = (variable) => {
        if (activeField === 'system_prompt' && systemPromptRef) {
            insertAtCursor(systemPromptRef, variable, 'system_prompt');
        } else if (activeField === 'content' && contentRef) {
            insertAtCursor(contentRef, variable, 'content');
        }
        setVariablesWindowOpen(false);
    };

    const insertAtCursor = (ref, text, field) => {
        const input = ref;
        if (!input) return;
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const value = template[field];
        const newValue = value.slice(0, start) + text + value.slice(end);
        setTemplate(prev => ({
            ...prev,
            [field]: newValue
        }));
        // Move cursor after inserted text
        setTimeout(() => {
            input.focus();
            input.setSelectionRange(start + text.length, start + text.length);
        }, 0);
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
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
                        Edit Template
                    </Typography>
                    <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => setShowDeleteConfirm(true)}
                        disabled={deleting}
                    >
                        Delete Template
                    </Button>
                </Box>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <form onSubmit={handleSubmit}>
                    <TextField
                        label="Template Name"
                        name="template_name"
                        value={template.template_name}
                        onChange={handleInputChange}
                        fullWidth
                        required
                        sx={{ mb: 2 }}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Template Type</InputLabel>
                        <Select
                            label="Template Type"
                            name="template_type"
                            value={template.template_type}
                            onChange={handleInputChange}
                            required
                        >
                            <MenuItem value="Selection">Selection</MenuItem>
                            <MenuItem value="Extraction">Extraction</MenuItem>
                            <MenuItem value="Response">Response</MenuItem>
                        </Select>
                    </FormControl>
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>System Prompt</Typography>
                    <TextField
                        label="System Prompt"
                        name="system_prompt"
                        value={template.system_prompt}
                        onChange={handleInputChange}
                        fullWidth
                        multiline
                        minRows={3}
                        inputRef={ref => setSystemPromptRef(ref)}
                        sx={{ mb: 1 }}
                    />
                    <Button
                        size="small"
                        variant="outlined"
                        sx={{ mt: 0, mb: 2 }}
                        onClick={() => {
                            setActiveField('system_prompt');
                            setVariablesWindowOpen(true);
                        }}
                    >
                        Insert Variable
                    </Button>
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>Template Content</Typography>
                    <TextField
                        label="Template Content"
                        name="content"
                        value={template.content}
                        onChange={handleInputChange}
                        fullWidth
                        multiline
                        minRows={6}
                        inputRef={ref => setContentRef(ref)}
                        sx={{ mb: 1 }}
                        required
                    />
                    <Button
                        size="small"
                        variant="outlined"
                        sx={{ mt: 0, mb: 2 }}
                        onClick={() => {
                            setActiveField('content');
                            setVariablesWindowOpen(true);
                        }}
                    >
                        Insert Variable
                    </Button>
                    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            disabled={saving}
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={() => navigate(-1)}
                            disabled={saving}
                        >
                            Cancel
                        </Button>
                    </Box>
                </form>
            </Paper>

            <Dialog
                open={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
            >
                <DialogTitle>Confirm Delete</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to delete this template? This action cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowDeleteConfirm(false)} color="primary">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleDelete}
                        color="error"
                        variant="contained"
                        disabled={deleting}
                    >
                        {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>

            <TemplateVariablesWindow
                open={variablesWindowOpen}
                onClose={() => setVariablesWindowOpen(false)}
                onVariableSelect={handleVariableSelect}
            />
        </Box>
    );
}

export default TemplateEdit;