import React, { useState, useEffect, useRef } from 'react';
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
    IconButton,
    Tooltip,
    Stack,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import VariableIcon from '@mui/icons-material/Code';
import { API_CONFIG, AUTH_CONFIG } from '../../config';
import TemplateVariablesWindow from './TemplateVariablesWindow';
import axios from 'axios';

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
    const [variables, setVariables] = useState([]);
    const [variablesLoading, setVariablesLoading] = useState(false);

    // Variables window state
    const [variablesWindowOpen, setVariablesWindowOpen] = useState(false);
    const [activeField, setActiveField] = useState(null); // 'system_prompt' or 'content'
    const contentRef = useRef(null);
    const systemPromptRef = useRef(null);

    const adminApiKey = sessionStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.ADMIN_API_KEY);

    const [testUserId, setTestUserId] = useState('');
    const [testResult, setTestResult] = useState(null);
    const [testLoading, setTestLoading] = useState(false);
    const [testError, setTestError] = useState(null);

    useEffect(() => {
        const fetchTemplate = async () => {
            if (!businessId || !templateId || !adminApiKey) {
                setError('Missing required parameters');
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}?business_id=${businessId}`, {
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
                    template_type: data.template_type ? data.template_type.toLowerCase() : '',
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

    useEffect(() => {
        const loadVariables = async () => {
            if (!businessId || !adminApiKey) return;
            
            setVariablesLoading(true);
            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/api/template-variables/available/`, {
                    headers: {
                        'Authorization': `Bearer ${adminApiKey}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch template variables');
                }

                const data = await response.json();
                setVariables(data);
            } catch (err) {
                console.error('Error loading variables:', err);
                setError('Failed to load template variables. Some features may be limited.');
            } finally {
                setVariablesLoading(false);
            }
        };

        loadVariables();
    }, [businessId, adminApiKey]);

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setTemplate(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
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

            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}`, {
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
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        setDeleting(true);
        setError(null);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEMPLATES}/${templateId}?business_id=${businessId}`, {
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

            navigate(`/business/${businessId}/stages?agent_id=${agentId}`);
        } catch (err) {
            console.error('Error deleting template:', err);
            setError(`Failed to delete template: ${err.message}`);
        } finally {
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    };

    // Enhanced variable selection handler
    const handleVariableSelect = (variable) => {
        console.log('Handling variable selection:', { variable, activeField });
        const activeRef = activeField === 'system_prompt' ? systemPromptRef : contentRef;
        
        if (!activeRef.current) {
            console.error('Active ref not found for field:', activeField);
            return;
        }

        try {
            const input = activeRef.current;
            const start = input.selectionStart;
            const end = input.selectionEnd;
            const value = template[activeField];
            
            // Validate variable format
            if (!variable.startsWith('{{') || !variable.endsWith('}}')) {
                throw new Error('Invalid variable format');
            }

            const newValue = value.slice(0, start) + variable + value.slice(end);
            
            console.log('Inserting variable:', {
                field: activeField,
                start,
                end,
                variable,
                newValue
            });

            setTemplate(prev => ({
                ...prev,
                [activeField]: newValue
            }));

            // Move cursor after inserted text
            setTimeout(() => {
                input.focus();
                input.setSelectionRange(start + variable.length, start + variable.length);
            }, 0);

            setSuccess('Variable inserted successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            console.error('Error inserting variable:', err);
            setError('Failed to insert variable. Please try again.');
            setTimeout(() => setError(null), 3000);
        } finally {
            setVariablesWindowOpen(false);
        }
    };

    const handleOpenVariablesWindow = (field) => {
        setActiveField(field);
        setVariablesWindowOpen(true);
    };

    const handleTestTemplate = async () => {
        setTestLoading(true);
        setTestError(null);
        setTestResult(null);
        try {
            const response = await axios.post('/api/template-test', {
                business_id: businessId,
                agent_id: agentId,
                user_id: testUserId,
                template_id: templateId
            });
            setTestResult(response.data);
        } catch (err) {
            setTestError(err.response?.data?.message || err.message || 'Failed to test template.');
        } finally {
            setTestLoading(false);
        }
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
            {/* Debugging info */}
            <Box sx={{ mb: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                <Typography variant="caption" color="secondary">DEBUG INFO:</Typography>
                <Typography variant="caption">adminApiKey: {adminApiKey ? adminApiKey.substring(0, 8) + '...' : 'NOT SET'}</Typography><br/>
                <Typography variant="caption">variablesLoading: {String(variablesLoading)}</Typography><br/>
                <Typography variant="caption">variables: {JSON.stringify(variables)}</Typography>
            </Box>

            <Button 
                onClick={() => navigate(`/business/${businessId}/stages?agent_id=${agentId}`)} 
                sx={{ mb: 2 }}
            >
                Back to Stages
            </Button>

            <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5">Edit Template</Typography>
                    <Stack direction="row" spacing={2}>
                        <Button
                            variant="outlined"
                            color="primary"
                            startIcon={<VariableIcon />}
                            onClick={() => handleOpenVariablesWindow('content')}
                        >
                            Insert Variable
                        </Button>
                        <Button
                            variant="outlined"
                            color="error"
                            startIcon={<DeleteIcon />}
                            onClick={() => setShowDeleteConfirm(true)}
                            disabled={deleting}
                        >
                            Delete Template
                        </Button>
                    </Stack>
                </Box>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

                <form onSubmit={handleSubmit}>
                    <Box sx={{ mb: 3 }}>
                        <TextField
                            fullWidth
                            label="Template Name"
                            name="template_name"
                            value={template.template_name}
                            onChange={handleInputChange}
                            required
                            sx={{ mb: 2 }}
                        />

                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Template Type</InputLabel>
                            <Select
                                name="template_type"
                                value={template.template_type}
                                onChange={handleInputChange}
                                label="Template Type"
                                required
                            >
                                <MenuItem value="selection">Selection</MenuItem>
                                <MenuItem value="extraction">Extraction</MenuItem>
                                <MenuItem value="response">Response</MenuItem>
                            </Select>
                        </FormControl>

                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Typography variant="subtitle1">System Prompt</Typography>
                                <Button
                                    startIcon={<VariableIcon />}
                                    onClick={() => handleOpenVariablesWindow('system_prompt')}
                                    size="small"
                                    sx={{ ml: 2 }}
                                >
                                    Insert Variable
                                </Button>
                            </Box>
                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                name="system_prompt"
                                value={template.system_prompt}
                                onChange={handleInputChange}
                                inputRef={systemPromptRef}
                                placeholder="Enter system prompt... Use the Insert Variable button to add template variables"
                            />
                        </Box>

                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Typography variant="subtitle1">Content</Typography>
                                <Button
                                    startIcon={<VariableIcon />}
                                    onClick={() => handleOpenVariablesWindow('content')}
                                    size="small"
                                    sx={{ ml: 2 }}
                                >
                                    Insert Variable
                                </Button>
                            </Box>
                            <TextField
                                fullWidth
                                multiline
                                rows={8}
                                name="content"
                                value={template.content}
                                onChange={handleInputChange}
                                inputRef={contentRef}
                                placeholder="Enter template content... Use the Insert Variable button to add template variables"
                            />
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                            <TextField
                                label="Test User ID"
                                value={testUserId}
                                onChange={e => setTestUserId(e.target.value)}
                                size="small"
                                placeholder="Enter user ID for test"
                            />
                            <Button
                                variant="contained"
                                color="info"
                                onClick={handleTestTemplate}
                                disabled={testLoading || !testUserId}
                            >
                                {testLoading ? <CircularProgress size={20} /> : 'Test'}
                            </Button>
                        </Box>

                        {testError && <Alert severity="error" sx={{ mb: 2 }}>{testError}</Alert>}
                        {testResult && (
                            <Paper sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
                                <Typography variant="subtitle1">Test Result:</Typography>
                                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{JSON.stringify(testResult, null, 2)}</pre>
                            </Paper>
                        )}

                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                            <Button
                                variant="outlined"
                                onClick={() => navigate(`/business/${businessId}/templates`)}
                            >
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                variant="contained"
                                disabled={loading || saving}
                            >
                                {saving ? <CircularProgress size={24} /> : 'Save Template'}
                            </Button>
                        </Box>
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
                    <Button onClick={() => setShowDeleteConfirm(false)}>Cancel</Button>
                    <Button onClick={handleDelete} color="error" disabled={deleting}>
                        {deleting ? <CircularProgress size={24} /> : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>

            <TemplateVariablesWindow
                open={variablesWindowOpen}
                onClose={() => setVariablesWindowOpen(false)}
                onVariableSelect={handleVariableSelect}
                variables={variables}
                loading={variablesLoading}
            />
        </Box>
    );
}

export default TemplateEdit; 