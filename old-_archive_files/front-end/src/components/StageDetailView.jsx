import React from 'react';
import {
    Card,
    CardContent,
    Typography,
    Grid,
    Divider,
    Box,
    CircularProgress,
    Button
} from '@mui/material';
import { useStageDetails } from '../hooks/useStageDetails';

function StageDetailView({ selectedStageId, handleSnackbarOpen }) {
    const { stageDetails, isLoading, error } = useStageDetails(selectedStageId, handleSnackbarOpen);

    let content;
    if (isLoading) {
        content = (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                <CircularProgress />
            </Box>
        );
    } else if (error) {
        content = (
            <Typography color="error" variant="body1">
                {error}
            </Typography>
        );
    } else if (!stageDetails) {
        content = (
            <Typography variant="body1">
                No stage selected. Please select a stage to view its details.
            </Typography>
        );
    } else {
        content = (
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="subtitle1" color="primary">Basic Information</Typography>
                    <Typography variant="body1"><strong>Stage ID:</strong> {stageDetails.stage_id}</Typography>
                    <Typography variant="body1"><strong>Name:</strong> {stageDetails.stage_name}</Typography>
                    <Typography variant="body1"><strong>Type:</strong> {stageDetails.stage_type}</Typography>
                    <Typography variant="body1"><strong>Description:</strong> {stageDetails.stage_description}</Typography>
                </Grid>
                
                <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle1" color="primary">Template IDs</Typography>
                    <Typography variant="body1">
                        <strong>Stage Selection Template:</strong> {stageDetails.stage_selection_template_id || 'Not configured'}
                    </Typography>
                    <Typography variant="body1">
                        <strong>Data Extraction Template:</strong> {stageDetails.data_extraction_template_id || 'Not configured'}
                    </Typography>
                    <Typography variant="body1">
                        <strong>Response Generation Template:</strong> {stageDetails.response_generation_template_id || 'Not configured'}
                    </Typography>
                </Grid>

                {stageDetails.created_at && (
                    <Grid item xs={12}>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="body2" color="textSecondary">
                            Created: {new Date(stageDetails.created_at).toLocaleString()}
                        </Typography>
                    </Grid>
                )}
            </Grid>
        );
    }

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                        Stage Details {stageDetails ? `(${stageDetails.stage_name || selectedStageId})` : ''}
                    </Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {content}
            </CardContent>
        </Card>
    );
}

export default StageDetailView;