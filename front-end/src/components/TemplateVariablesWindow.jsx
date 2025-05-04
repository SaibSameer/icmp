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
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SearchIcon from '@mui/icons-material/Search';
import { getTemplateVariables } from '../services/templateService';

function TemplateVariablesWindow({ open, onClose, onVariableSelect }) {
    const [variables, setVariables] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (open) {
            fetchVariables();
        }
    }, [open]);

    const fetchVariables = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await getTemplateVariables();
            setVariables(response);
        } catch (err) {
            console.error("Failed to fetch variables:", err);
            setError('Failed to fetch template variables. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleVariableClick = (variable) => {
        if (onVariableSelect) {
            onVariableSelect(`{{${variable.variable_name}}}`);
        }
    };

    const handleCopyVariable = (variable) => {
        navigator.clipboard.writeText(`{{${variable.variable_name}}}`);
    };

    const renderExampleValue = (value) => {
        if (typeof value === 'object' && value !== null) {
            if (Array.isArray(value)) {
                return value.map((item, index) => (
                    <Typography key={index} variant="caption" color="text.secondary">
                        {typeof item === 'object' ? JSON.stringify(item) : item}
                    </Typography>
                ));
            } else {
                return (
                    <Typography variant="caption" color="text.secondary">
                        {JSON.stringify(value)}
                    </Typography>
                );
            }
        }
        return (
            <Typography variant="caption" color="text.secondary">
                {value}
            </Typography>
        );
    };

    const filteredVariables = variables.filter(variable =>
        variable.variable_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        variable.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
        >
            <DialogTitle>
                <Typography variant="subtitle1" component="div">Available Template Variables</Typography>
                <TextField
                    fullWidth
                    variant="outlined"
                    size="small"
                    placeholder="Search variables..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    sx={{ mt: 1 }}
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
                    <Typography color="error" sx={{ mb: 2 }}>
                        {error}
                    </Typography>
                )}
                {loading ? (
                    <Box display="flex" justifyContent="center" p={2}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <List>
                        {filteredVariables.map((variable) => (
                            <ListItem
                                key={variable.variable_id}
                                button
                                onClick={() => handleVariableClick(variable)}
                                secondaryAction={
                                    <Tooltip title="Copy variable">
                                        <IconButton
                                            edge="end"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleCopyVariable(variable);
                                            }}
                                        >
                                            <ContentCopyIcon />
                                        </IconButton>
                                    </Tooltip>
                                }
                            >
                                <ListItemText
                                    primary={`{{${variable.variable_name}}}`}
                                    secondary={
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">
                                                {variable.description}
                                            </Typography>
                                            {variable.example_value && (
                                                <Box sx={{ mt: 0.5 }}>
                                                    <Typography variant="caption" color="text.secondary">
                                                        Example: {renderExampleValue(variable.example_value)}
                                                    </Typography>
                                                </Box>
                                            )}
                                        </Box>
                                    }
                                />
                            </ListItem>
                        ))}
                        {filteredVariables.length === 0 && (
                            <Typography sx={{ p: 2, textAlign: 'center' }}>
                                No variables found matching your search.
                            </Typography>
                        )}
                    </List>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}

export default TemplateVariablesWindow;