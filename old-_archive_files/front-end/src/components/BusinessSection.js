import React from 'react';
import {
    Typography,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
    Alert,
    Box
} from '@mui/material';
import useBusiness from '../hooks/useBusiness';

function BusinessSection({ handleSnackbarOpen }) {
    const { businessDetails, isLoading, error } = useBusiness(handleSnackbarOpen);

    let content;

    if (isLoading) {
        content = (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100px' }} data-testid="loading-state">
                <CircularProgress />
                <Typography sx={{ ml: 1 }}>Loading Business Details...</Typography>
            </Box>
        );
    } else if (error) {
        content = <Alert severity="error" data-testid="error-state">Error loading business details: {error}</Alert>;
    } else if (businessDetails) {
        content = (
            <List dense>
                <ListItem>
                    <ListItemText primary="Business Name" secondary={businessDetails.business_name || 'N/A'} />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Address" secondary={businessDetails.address || 'N/A'} />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Phone" secondary={businessDetails.phone || 'N/A'} />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Email" secondary={businessDetails.email || 'N/A'} />
                </ListItem>
            </List>
        );
    } else {
        content = <Typography variant="body2" data-testid="empty-state">Business details will load here.</Typography>;
    }

    return (
        <Card sx={{ mt: 2 }} data-testid="business-details">
            <CardContent>
                <Typography variant="h6" gutterBottom>Business Details</Typography>
                {content}
            </CardContent>
        </Card>
    );
}

export default BusinessSection;