import React, { useState } from 'react';
import { TextField, Button, Typography, Card, CardContent, Box, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/authService';
import { API_CONFIG } from '../config';

function Login({ 
    setIsAuthenticated, 
    handleSnackbarOpen,
    setUserId: setParentUserId,
    setBusinessId: setParentBusinessId,
    setBusinessApiKey: setParentBusinessApiKey
}) {
    const [isLoading, setIsLoading] = useState(false);
    const [userId, setUserId] = useState('');
    const [businessId, setBusinessId] = useState(API_CONFIG.DEFAULTS.BUSINESS_ID);
    const [businessApiKey, setBusinessApiKey] = useState(API_CONFIG.DEFAULTS.API_KEY);
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);

        try {
            // Validate and save credentials using the authService
            const data = await login(userId, businessId, businessApiKey);

            if (data.success) {
                // Update parent state
                setParentUserId(userId.trim());
                setParentBusinessId(businessId.trim());
                setParentBusinessApiKey(businessApiKey.trim());

                // Set authentication state
                setIsAuthenticated(true);
                
                // Show success message and redirect
                handleSnackbarOpen(data.message || 'Login successful', 'success');
                navigate('/business');
            } else {
                // Show error message
                handleSnackbarOpen(data.message || 'Login failed', 'error');
                setIsAuthenticated(false);
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
                        label="Business ID" 
                        variant="outlined" 
                        value={businessId}
                        onChange={(e) => setBusinessId(e.target.value)}
                        disabled={isLoading}
                        required
                        error={!businessId}
                        helperText={!businessId ? "Business ID is required" : ""}
                        fullWidth
                    />
                    <TextField
                        label="Business API Key"
                        variant="outlined"
                        value={businessApiKey}
                        onChange={(e) => setBusinessApiKey(e.target.value)}
                        disabled={isLoading}
                        type="password"
                        required
                        error={!businessApiKey}
                        helperText={!businessApiKey ? "Business API Key is required" : ""}
                        fullWidth
                    />
                    <TextField 
                        label="User ID" 
                        variant="outlined" 
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        disabled={isLoading}
                        required
                        error={!userId}
                        helperText={!userId ? "User ID is required" : ""}
                        fullWidth
                    />

                    <Button 
                        type="submit"
                        variant="contained" 
                        disabled={isLoading || !userId || !businessId || !businessApiKey}
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