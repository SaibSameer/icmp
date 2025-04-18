// File: src/components/BusinessManagement.js
// Last Modified: 2026-03-29

import React, { useState } from 'react';
import { TextField, Button, Typography, Card, CardContent, Box } from '@mui/material';
import { fetchBusinessDetails as fetchBusinessDetailsApi } from '../services/testService';

function BusinessManagement({ businessName, setBusinessName, businessOutput, setBusinessOutput, fetchBusinessDetails, handleSnackbarOpen, apiKey, businessId, }) {
    const handleFetchBusinessDetails = async () => {
        if (!businessId) {
            setBusinessOutput("Please enter a Business ID.");
            handleSnackbarOpen("Please enter a Business ID.", "warning")
            return;
        }
        try {
            const response = await fetchBusinessDetailsApi(businessId, apiKey)
            //setBusinessOutput("Business endpoint not implemented yet.");

            setBusinessOutput(JSON.stringify(response, null, 2)); // this data will be displayed in json form
            handleSnackbarOpen("Business endpoint Fetched!", "info")

        } catch (error) {
            setBusinessOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Business Management</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextField label="Business Name" variant="outlined" value={businessName} onChange={(e) => setBusinessName(e.target.value)} />
                    <Button variant="contained" onClick={() => console.log("Create Business not yet implemented")}>Create Business</Button>
                    <Button variant="contained" onClick={handleFetchBusinessDetails}>Fetch Business Details</Button>
                    <Typography variant="body1">{businessOutput}</Typography>
                </Box>
            </CardContent>
        </Card>
    );
}

export default BusinessManagement;