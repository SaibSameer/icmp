import React from 'react';
import { TextField, Button, Typography, Card, CardContent, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Configuration = ({
    userId,
    setUserId,
    businessId,
    setBusinessId,
    businessApiKey,
    setBusinessApiKey,
    handleSnackbarOpen,
    handleLogout
}) => {
    const navigate = useNavigate();

    const handleSave = async () => {
        if (!userId || !businessId || !businessApiKey) {
            handleSnackbarOpen('Please enter all the configuration values', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/save-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    userId,
                    businessId,
                    businessApiKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                handleSnackbarOpen(data.message || 'Invalid credentials', 'error');
                return;
            }

            handleSnackbarOpen('Configuration saved successfully', 'success');
            navigate('/business');
        } catch (error) {
            handleSnackbarOpen('Error saving configuration', 'error');
        }
    };

    const onLogout = () => {
        handleLogout();
        navigate('/login');
    };

    return (
        <Card>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Configuration</Typography>
                    <Button variant="outlined" color="secondary" onClick={onLogout}>
                        Logout
                    </Button>
                </Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                        label="Business API Key"
                        type="password"
                        value={businessApiKey}
                        onChange={(e) => setBusinessApiKey(e.target.value)}
                        required
                        error={!businessApiKey}
                        helperText={!businessApiKey ? 'Business API Key is required' : ''}
                        data-testid="business-api-key-input"
                    />
                    <TextField
                        label="User ID"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        required
                        error={!userId}
                        helperText={!userId ? 'User ID is required' : ''}
                        data-testid="user-id-input"
                    />
                    <TextField
                        label="Business ID"
                        value={businessId}
                        onChange={(e) => setBusinessId(e.target.value)}
                        required
                        error={!businessId}
                        helperText={!businessId ? 'Business ID is required' : ''}
                        data-testid="business-id-input"
                    />
                    <Button variant="contained" color="primary" onClick={handleSave}>
                        Save Config
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default Configuration;