import React, { useState, useEffect } from 'react';
import { Box, Typography, List, ListItem, ListItemButton, ListItemText, CircularProgress, Alert } from '@mui/material';
import { useBusinessContext } from '../context/BusinessContext';
import { API_CONFIG } from '../config'; // Assuming you have API config
import { useNavigate } from 'react-router-dom'; // Import useNavigate

function BusinessList() {
    const [businesses, setBusinesses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { setSelectedBusinessId, selectedBusinessId } = useBusinessContext();
    const navigate = useNavigate(); // Get the navigate function

    useEffect(() => {
        const fetchBusinesses = async () => {
            setLoading(true);
            setError(null);
            const adminApiKey = sessionStorage.getItem('adminApiKey');

            if (!adminApiKey) {
                setError('Admin API Key not found. Please configure it first.');
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/`, {
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

                const data = await response.json();
                setBusinesses(data || []);
            } catch (err) {
                console.error("Failed to fetch businesses:", err);
                setError(`Failed to fetch businesses: ${err.message}`);
                setBusinesses([]); // Clear businesses on error
            } finally {
                setLoading(false);
            }
        };

        fetchBusinesses();
    }, []); // Fetch only once on mount

    const handleSelectBusiness = (id) => {
        setSelectedBusinessId(id);
        console.log("Selected Business ID:", id); // For debugging
        navigate(`/business/${id}`); // Navigate to the detail page
    };

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>;
    }

    return (
        <Box sx={{ mt: 2 }}>
            <Typography variant="h5" gutterBottom>
                Select a Business
            </Typography>
            {businesses.length === 0 ? (
                <Typography>No businesses found.</Typography>
            ) : (
                <List component="nav" aria-label="businesses list">
                    {businesses.map((business) => (
                        <ListItem 
                            key={business.business_id} 
                            disablePadding
                            selected={selectedBusinessId === business.business_id}
                        >
                            <ListItemButton onClick={() => handleSelectBusiness(business.business_id)}>
                                <ListItemText 
                                    primary={business.business_name}
                                    secondary={`ID: ${business.business_id}`}
                                />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            )}
        </Box>
    );
}

export default BusinessList;