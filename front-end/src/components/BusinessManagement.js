// src/components/BusinessManagement.js
import React from 'react';
import { TextField, Button, Typography, Card, CardContent, Box } from '@mui/material';

function BusinessManagement({
    businessName,
    setBusinessName,
    businessOutput,
    setBusinessOutput,
     fetchBusinessDetails,
    handleSnackbarOpen,
    apiKey,
    businessId,
}) {
    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Business Management</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextField
                        label="Business Name"
                        variant="outlined"
                        value={businessName}
                        onChange={(e) => setBusinessName(e.target.value)}
                    />
                    <Button variant="contained" onClick={() => console.log("Create Business not yet implemented")}>
                        Create Business
                    </Button>
                    <Button variant="contained" onClick={fetchBusinessDetails}>
                        Fetch Business Details
                    </Button>
                    <Typography variant="body1">{businessOutput}</Typography>
                </Box>
            </CardContent>
        </Card>
    );
}

export default BusinessManagement;