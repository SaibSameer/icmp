import React, { useState } from 'react';
import { TextField, Button, Typography, Card, CardContent, Box, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG, AUTH_CONFIG } from '../config';
import { login } from '../services/authService';

function Login({ 
    setIsAuthenticated, 
    handleSnackbarOpen,
    setUserId,
    setBusinessId,
    setBusinessApiKey
}) {
    const [isLoading, setIsLoading] = useState(false);
    const [userIdInput, setUserIdInput] = useState(API_CONFIG.DEFAULTS.USER_ID);
    const [businessIdInput, setBusinessIdInput] = useState(API_CONFIG.DEFAULTS.BUSINESS_ID);
    const [businessApiKeyInput, setBusinessApiKeyInput] = useState(API_CONFIG.DEFAULTS.API_KEY);
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);

        // Trim inputs to avoid whitespace issues
        const trimmedUserId = userIdInput.trim();
        const trimmedBusinessId = businessIdInput.trim();
        const trimmedBusinessApiKey = businessApiKeyInput.trim();

        try {
            console.log('Logging in with:', {
                userId: trimmedUserId,
                businessId: trimmedBusinessId,
                businessApiKey: trimmedBusinessApiKey
            });

            const data = await login(trimmedUserId, trimmedBusinessId, trimmedBusinessApiKey);
            
            if (data.success) {
                // Update parent state
                setUserId(trimmedUserId);
                setBusinessId(trimmedBusinessId);
                setBusinessApiKey(trimmedBusinessApiKey);

                handleSnackbarOpen('Login successful', 'success');
                setIsAuthenticated(true);
                navigate('/');
            } else {
                throw new Error(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            handleSnackbarOpen(error.message || 'Login failed', 'error');
            setIsAuthenticated(false);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card sx={{ mt: 4, maxWidth: 400, mx: 'auto' }}>
            <CardContent>
                <Typography variant="h5" gutterBottom align="center">
                    Login
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextField 
                        label="User ID" 
                        variant="outlined" 
                        value={userIdInput}
                        onChange={(e) => setUserIdInput(e.target.value)}
                        disabled={isLoading}
                        required
                        error={!userIdInput}
                        helperText={!userIdInput ? "User ID is required" : ""}
                        fullWidth
                    />
                    <TextField 
                        label="Business ID" 
                        variant="outlined" 
                        value={businessIdInput}
                        onChange={(e) => setBusinessIdInput(e.target.value)}
                        disabled={isLoading}
                        required
                        error={!businessIdInput}
                        helperText={!businessIdInput ? "Business ID is required" : ""}
                        fullWidth
                    />
                    <TextField
                        label="Business API Key"
                        variant="outlined"
                        value={businessApiKeyInput}
                        onChange={(e) => setBusinessApiKeyInput(e.target.value)}
                        disabled={isLoading}
                        type="password"
                        required
                        error={!businessApiKeyInput}
                        helperText={!businessApiKeyInput ? "Business API Key is required" : ""}
                        fullWidth
                    />
                    <Button 
                        type="submit" 
                        variant="contained" 
                        color="primary" 
                        disabled={isLoading}
                        fullWidth
                    >
                        {isLoading ? <CircularProgress size={24} /> : 'Login'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
}

export default Login;