import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';
import { API_CONFIG } from '../config';

function Configuration() {
    const navigate = useNavigate();
    const [adminApiKey, setAdminApiKey] = useState('');
    const [userId, setUserId] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const isAdminAuthenticated = !!sessionStorage.getItem('adminApiKey');

    useEffect(() => {
        setError('');
        setSuccess('');
        const storedKey = sessionStorage.getItem('adminApiKey');
        if (storedKey) {
            setAdminApiKey(storedKey);
        }
    }, []);

    const handleAdminLogin = async () => {
        setError('');
        setSuccess('');
        if (!adminApiKey) {
            setError('Admin API Key is required.');
            return;
        }
        
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/admin-check`, {
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

            sessionStorage.setItem('adminApiKey', adminApiKey);
            setSuccess('Admin API Key validated and saved for session.');
            
        } catch (err) {
            console.error("Admin validation failed:", err);
            setError(`Admin validation failed: ${err.message}`);
            sessionStorage.removeItem('adminApiKey');
        }
    };

    const handleAdminLogout = () => {
        setAdminApiKey('');
        sessionStorage.removeItem('adminApiKey');
        setSuccess('Admin logged out.');
        setError('');
    };

    return (
        <Box sx={{ mt: 4, p: 2, border: '1px solid grey', borderRadius: '4px' }}>
            <Typography variant="h6" gutterBottom>
                Admin Configuration
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

            {!isAdminAuthenticated ? (
                <Box component="form" noValidate autoComplete="off">
                     <TextField
                        label="Admin Master API Key"
                        variant="outlined"
                        type="password"
                        fullWidth
                        value={adminApiKey}
                        onChange={(e) => setAdminApiKey(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField 
                        label="Admin User ID (Optional)"
                        variant="outlined"
                        fullWidth
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                   
                    <Button variant="contained" onClick={handleAdminLogin} sx={{ mr: 1 }}>
                        Validate & Save Admin Key
                    </Button>
                    <Button variant="outlined" onClick={() => navigate('/')}>
                         View All Businesses
                    </Button>
                </Box>
            ) : (
                <Box>
                    <Typography sx={{ mb: 2 }}>Admin key is configured for this session.</Typography>
                    <Button variant="outlined" onClick={handleAdminLogout} sx={{ mr: 1 }}>
                        Clear Admin Key (Logout)
                    </Button>
                    <Button variant="outlined" onClick={() => navigate('/')}>
                         View All Businesses
                    </Button>
                </Box>
            )}
        </Box>
    );
}

export default Configuration;