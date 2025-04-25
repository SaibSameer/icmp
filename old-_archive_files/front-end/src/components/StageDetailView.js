import React from 'react';
import {
    Typography,
    Card,
    CardContent,
    Box,
    TextField, // Use TextField for consistent layout, make read-only for now
    CircularProgress,
    Alert,
    Grid, // For layout
    Divider
} from '@mui/material';
import useStageDetails from '../hooks/useStageDetails'; // Import the hook

function StageDetailView({ selectedStageId, handleSnackbarOpen }) {
    // Use the hook to get details for the selected stage
    const { stageDetails, isLoading, error } = useStageDetails(selectedStageId, handleSnackbarOpen);

    // Define common TextField props for read-only view
    const textFieldProps = {
        variant: "outlined",
        fullWidth: true,
        InputProps: {
            readOnly: true, // Make fields read-only for now
        },
        size: "small",
        margin: "dense" // Adjust spacing
    };

    // Content to render based on loading/error/data state
    let content;
    if (!selectedStageId) {
        // This component should ideally not be rendered if no stage is selected,
        // but handle the case defensively.
        content = null; // Or a placeholder like <Typography>Select a stage</Typography>
    } else if (isLoading) {
        content = (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 3 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading Stage Details...</Typography>
            </Box>
        );
    } else if (error) {
        content = <Alert severity="error" sx={{ m: 1 }}>Error loading stage details: {error}</Alert>;
    } else if (stageDetails) {
        // Assuming stageDetails object structure from typical API response
        content = (
            <Box>
                <Grid container spacing={1}>
                     {/* Basic Stage Info */}
                     <Grid item xs={12} sm={6}>
                        <TextField
                            label="Stage ID"
                            value={stageDetails.stage_id || ''}
                            {...textFieldProps}
                        />
                    </Grid>
                     <Grid item xs={12} sm={6}>
                        <TextField
                            label="Stage Name"
                            value={stageDetails.stage_name || ''}
                            {...textFieldProps}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            label="Stage Type"
                            value={stageDetails.stage_type || ''}
                            {...textFieldProps}
                            // Potentially map type ID/code to a user-friendly name later
                        />
                    </Grid>
                    <Grid item xs={12}>
                         <TextField
                            label="Description"
                            value={stageDetails.description || ''}
                            multiline
                            rows={2} // Adjust as needed
                            {...textFieldProps}
                        />
                    </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" gutterBottom>Associated Templates</Typography>
                <Grid container spacing={1}>
                    {/* Template IDs */}
                    <Grid item xs={12} sm={4}>
                        <TextField
                            label="Selection Template ID"
                            value={stageDetails.selection_template_id || 'None'}
                            {...textFieldProps}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            label="Extraction Template ID"
                            value={stageDetails.extraction_template_id || 'None'}
                            {...textFieldProps}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            label="Response Template ID"
                            value={stageDetails.response_template_id || 'None'}
                            {...textFieldProps}
                        />
                    </Grid>
                </Grid>

                {/* Placeholder for Template Management Windows */}
                {/* <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1">Template Editors (Coming Soon)</Typography>
                {/* ... */}

                {/* Placeholder for Prompt Preview */}
                {/* <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1">Prompt Preview (Coming Soon)</Typography>
                {/* ... */}
            </Box>
        );
    } else {
        // Should not happen if selectedStageId is valid but data is null after loading without error
        content = <Typography variant="body2" sx={{ p: 2 }}>No details available for this stage.</Typography>;
    }

    // Only render the card if a stage is selected
    if (!selectedStageId) {
        return null;
    }

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                 {/* Add Edit button later */}
                <Typography variant="h6" gutterBottom>
                    Stage Details {stageDetails ? `(${stageDetails.stage_name || selectedStageId})` : ''}
                </Typography>
                 <Divider sx={{ mb: 2 }} />
                {content}
            </CardContent>
        </Card>
    );
}

export default StageDetailView;