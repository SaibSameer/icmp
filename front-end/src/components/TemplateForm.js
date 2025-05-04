import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, TextField, Button, Select, MenuItem, FormControl, InputLabel, Checkbox, FormControlLabel, Paper, CircularProgress, Alert, Chip, Divider } from '@mui/material';
import { API_CONFIG } from '../config';

function TemplateForm() {
    const { businessId } = useParams(); // Get businessId from route parameter
    const navigate = useNavigate();
    const adminApiKey = sessionStorage.getItem('adminApiKey');

    const [templateData, setTemplateData] = useState({
        template_name: '',
        content: '',
        system_prompt: '',
        template_type: 'selection', // Default type
        is_default: false,
    });
    const [extractedVariables, setExtractedVariables] = useState([]); // State for variables
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Define the helper strings outside JSX
    const variableSyntaxExample = '{{variable_name}}';
    const helperTextString = `Use ${variableSyntaxExample} syntax for variables.`;
    const noVariablesDetectedString = `No variables detected (use '${variableSyntaxExample}')`;

    // Check if businessId is available
    useEffect(() => {
        if (!businessId) {
            setError('Business ID is missing from the URL. Cannot create template.');
            // Optionally navigate back or show a persistent error
        }
    }, [businessId]);

    // Function to extract variables (like {{var_name}})
    const extractVariables = (text) => {
        if (!text) return [];
        // Regex to find {{variable_name}} patterns
        const regex = /\{\{([^}]+)\}\}/g;
        const matches = text.match(regex) || [];
        // Return unique variable names without the braces
        const uniqueVars = [...new Set(matches.map(match => match.slice(2, -2).trim()))];
        return uniqueVars.filter(v => v); // Filter out empty strings
    };

    // Update extractedVariables whenever content changes
    useEffect(() => {
        const variables = extractVariables(templateData.content);
        setExtractedVariables(variables);
    }, [templateData.content]);

    const handleInputChange = (event) => {
        const { name, value, type, checked } = event.target;
        setTemplateData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault(); // Prevent default form submission
        setError('');
        setSuccess('');

        if (!businessId) {
             setError('Business ID is missing. Cannot create template.');
             return;
        }
        if (!templateData.template_name || !templateData.content || !templateData.template_type) {
            setError('Template Name, Content (Prompt), and Type are required.');
            return;
        }
        if (!adminApiKey) {
            setError('Admin API Key not found. Please configure it first.');
            return;
        }

        const payload = { ...templateData, business_id: businessId };
        console.log("Submitting new template:", payload);
        setLoading(true);

        try {
            const apiUrl = `${API_CONFIG.BASE_URL}/templates`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                   'Authorization': `Bearer ${adminApiKey}`,
                   'Content-Type': 'application/json',
                   'Accept': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                const message = errorData.message || `HTTP error ${response.status}`;
                console.error("Failed to add template:", message, errorData);
                throw new Error(message);
            }
            
            setSuccess(`Template '${payload.template_name}' created successfully! You can now close this page or create another.`);
            // Reset form after successful submission
            setTemplateData({
                template_name: '',
                content: '',
                system_prompt: '',
                template_type: 'selection',
                is_default: false,
            }); 

        } catch (err) {
           console.error("Error adding template:", err);
           setError(`Failed to add template: ${err.message}. Please check the details and try again.`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h5" gutterBottom>
                Create New Template for Business: {businessId || 'Error: Missing ID'}
            </Typography>
            
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

            <Box component="form" onSubmit={handleSubmit} noValidate>
                <TextField
                    required
                    fullWidth
                    margin="normal"
                    label="Template Name"
                    name="template_name"
                    value={templateData.template_name}
                    onChange={handleInputChange}
                    disabled={loading || !businessId}
                    error={!templateData.template_name && !!error} // Basic error indication
                />
                <TextField
                    required
                    fullWidth
                    margin="normal"
                    label="Content (Prompt)"
                    name="content"
                    multiline
                    rows={10}
                    value={templateData.content}
                    onChange={handleInputChange}
                    disabled={loading || !businessId}
                    error={!templateData.content && !!error}
                    helperText={helperTextString}
                />
                <Box sx={{ my: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Detected Variables:</Typography>
                    {extractedVariables.length > 0 ? (
                        extractedVariables.map(variable => (
                            <Chip label={variable} key={variable} sx={{ mr: 1, mb: 1 }} />
                        ))
                    ) : (
                        <Typography variant="body2" color="text.secondary">{noVariablesDetectedString}</Typography>
                    )}
                </Box>
                <Divider sx={{ my: 2 }}/>
                <TextField
                    fullWidth
                    margin="normal"
                    label="System Prompt (Optional)"
                    name="system_prompt"
                    multiline
                    rows={4}
                    value={templateData.system_prompt}
                    onChange={handleInputChange}
                    disabled={loading || !businessId}
                />
                <FormControl fullWidth margin="normal" required disabled={loading || !businessId}>
                    <InputLabel>Template Type</InputLabel>
                    <Select
                        name="template_type"
                        value={templateData.template_type}
                        label="Template Type"
                        onChange={handleInputChange}
                    >
                        <MenuItem value="selection">Selection</MenuItem>
                        <MenuItem value="extraction">Extraction</MenuItem>
                        <MenuItem value="generation">Generation</MenuItem>
                        {/* Add other types if applicable */}
                    </Select>
                </FormControl>
                <FormControlLabel
                    control={
                        <Checkbox
                            name="is_default"
                            checked={templateData.is_default}
                            onChange={handleInputChange}
                            disabled={loading || !businessId}
                        />
                    }
                    label="Is Default Template?"
                    sx={{ display: 'block', mt: 1 }}
                />

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={loading || !businessId || !templateData.template_name || !templateData.content}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Create Template'}
                    </Button>
                    <Button 
                        variant="outlined" 
                        onClick={() => navigate(`/business/${businessId}`)} // Navigate back to business detail
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                     {/* Optionally add a button to go back to stages list if agentId was available */}
                     {/* <Button variant="outlined" onClick={() => navigate(-1)}>Go Back</Button> */}
                </Box>
            </Box>
        </Paper>
    );
}

export default TemplateForm;