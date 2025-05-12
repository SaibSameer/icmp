import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    IconButton,
    TextField,
    InputAdornment,
    Tooltip,
    CircularProgress,
    Alert,
    Chip,
    Divider
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import templateService from '../../services/templateService';

const TemplateVariablesWindow = ({ open, onClose, onVariableSelect }) => {
    const [variables, setVariables] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [copiedVariable, setCopiedVariable] = useState(null);

    useEffect(() => {
        console.log('TemplateVariablesWindow mounted/updated');
        console.log('Dialog open state:', open);
        if (open) {
            console.log('Dialog opened, fetching variables...');
            fetchVariables();
        }
    }, [open]);

    const fetchVariables = async () => {
        console.log('Starting fetchVariables...');
        setLoading(true);
        setError(null);
        try {
            console.log('Calling templateService.getTemplateVariables()...');
            const data = await templateService.getTemplateVariables();
            console.log('Received template variables:', data);
            console.log('Number of variables received:', data.length);
            setVariables(data);
        } catch (err) {
            console.error('Error in fetchVariables:', err);
            console.error('Error details:', {
                message: err.message,
                stack: err.stack,
                name: err.name
            });
            setError(err.message || 'Failed to fetch template variables');
        } finally {
            setLoading(false);
            console.log('Fetch variables completed. Loading:', false);
        }
    };

    const handleVariableClick = (variable) => {
        try {
            const variableText = `{{${variable.variable_name}}}`;
            if (typeof onVariableSelect === 'function') {
                onVariableSelect(variableText);
            } else {
                throw new Error('onVariableSelect is not a function');
            }
        } catch (err) {
            console.error('Error selecting variable:', err);
            setError('Failed to select variable. Please try again.');
        }
    };

    const handleCopyVariable = (variable) => {
        try {
            const variableText = `{{${variable.variable_name}}}`;
            navigator.clipboard.writeText(variableText)
                .then(() => {
                    setCopiedVariable(variable.variable_name);
                    setTimeout(() => setCopiedVariable(null), 2000);
                })
                .catch(err => {
                    console.error('Failed to copy variable:', err);
                    setError('Failed to copy variable to clipboard');
                });
        } catch (err) {
            console.error('Error copying variable:', err);
            setError('Failed to copy variable. Please try again.');
        }
    };

    const renderExampleValue = (value) => {
        if (!value) return null;
        
        if (typeof value === 'object') {
            return (
                <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary" component="div">
                        Example:
                    </Typography>
                    <Typography variant="caption" color="text.secondary" component="pre" sx={{ 
                        mt: 0.5,
                        p: 1,
                        bgcolor: 'grey.100',
                        borderRadius: 1,
                        overflow: 'auto'
                    }}>
                        {JSON.stringify(value, null, 2)}
                    </Typography>
                </Box>
            );
        }
        
        return (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Example: {value}
            </Typography>
        );
    };

    const filteredVariables = variables.filter(variable =>
        (variable.variable_name && variable.variable_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (variable.description && variable.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    console.log('Current state:', {
        variablesCount: variables.length,
        filteredCount: filteredVariables.length,
        loading,
        error,
        searchTerm
    });

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    minHeight: '60vh',
                    maxHeight: '80vh'
                }
            }}
        >
            <DialogTitle>
                <Typography variant="h6" gutterBottom>
                    Available Template Variables
                </Typography>
                <TextField
                    fullWidth
                    variant="outlined"
                    size="small"
                    placeholder="Search variables..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                />
            </DialogTitle>
            <DialogContent>
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {loading ? (
                    <Box display="flex" justifyContent="center" alignItems="center" p={3}>
                        <CircularProgress />
                    </Box>
                ) : filteredVariables.length === 0 ? (
                    <Box p={2} textAlign="center">
                        <Typography color="text.secondary">
                            {searchTerm ? "No variables match your search" : "No variables available"}
                        </Typography>
                    </Box>
                ) : (
                    <List>
                        {filteredVariables.map((variable, index) => (
                            <React.Fragment key={variable.variable_name}>
                                {index > 0 && <Divider />}
                                <ListItem
                                    button
                                    onClick={() => handleVariableClick(variable)}
                                    sx={{
                                        py: 2,
                                        '&:hover': {
                                            bgcolor: 'action.hover'
                                        }
                                    }}
                                >
                                    <ListItemText
                                        primary={
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Typography variant="subtitle1">
                                                    {`{{${variable.variable_name}}}`}
                                                </Typography>
                                                {variable.required && (
                                                    <Chip
                                                        label="Required"
                                                        size="small"
                                                        color="primary"
                                                        variant="outlined"
                                                    />
                                                )}
                                            </Box>
                                        }
                                        secondary={
                                            <Box sx={{ mt: 1 }}>
                                                <Typography variant="body2" color="text.secondary">
                                                    {variable.description || 'No description available'}
                                                </Typography>
                                                {renderExampleValue(variable.example_value)}
                                            </Box>
                                        }
                                    />
                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        <Tooltip title={copiedVariable === variable.variable_name ? "Copied!" : "Copy variable"}>
                                            <IconButton
                                                edge="end"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleCopyVariable(variable);
                                                }}
                                                color={copiedVariable === variable.variable_name ? "primary" : "default"}
                                            >
                                                <ContentCopyIcon />
                                            </IconButton>
                                        </Tooltip>
                                        {variable.documentation && (
                                            <Tooltip title="View documentation">
                                                <IconButton
                                                    edge="end"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        window.open(variable.documentation, '_blank');
                                                    }}
                                                >
                                                    <InfoIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </ListItem>
                            </React.Fragment>
                        ))}
                    </List>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
};

export default TemplateVariablesWindow; 