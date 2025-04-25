import React, { useState } from 'react';
import {
    Typography,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
    Alert,
    Button,
    Box,
    Divider,
    IconButton // For potential Edit button
} from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import EditIcon from '@mui/icons-material/Edit'; // Example icon for Edit
import useStages from '../hooks/useStages'; // Import the hook we just created

// Define the StageSection component
function StageSection({ selectedAgentId, handleSnackbarOpen, onStageSelect }) {
    // Use the hook to get stages for the selected agent
    const { stages, isLoading, error, refreshStages } = useStages(selectedAgentId, handleSnackbarOpen);
    const [selectedStageId, setSelectedStageId] = useState(null);

    // Handler for selecting a stage
    const handleStageClick = (stageId) => {
        console.log("Selected Stage ID:", stageId);
        setSelectedStageId(stageId);
        if (onStageSelect) {
            onStageSelect(stageId); // Notify parent component
        }
    };

     // Handler for the Create New Stage button click
     const handleCreateStage = () => {
        // TODO: Implement logic to open a modal or form for creating a new stage
        console.log("Create New Stage clicked");
        handleSnackbarOpen("Create stage functionality not yet implemented.", "info");
    };

    // Handler for the Edit Stage button click
    const handleEditStage = (stageId, event) => {
        event.stopPropagation(); // Prevent triggering handleStageClick
        // TODO: Implement logic to open a modal or form for editing the stage
        console.log("Edit Stage clicked:", stageId);
        handleSnackbarOpen(`Edit stage (${stageId}) functionality not yet implemented.`, "info");
    };


    // Determine the content based on whether an agent is selected and loading/error states
    let content;
    if (!selectedAgentId) {
        content = <Typography variant="body2" sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>Please select an agent to view stages.</Typography>;
    } else if (isLoading) {
        content = (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 2 }}>
                <CircularProgress size={24} />
                <Typography sx={{ ml: 1 }} variant="body2">Loading Stages...</Typography>
            </Box>
        );
    } else if (error) {
        content = <Alert severity="error">Error loading stages: {error}</Alert>;
    } else if (stages.length > 0) {
        content = (
            <List dense>
                {stages.map((stage) => (
                    <ListItem
                        key={stage.stage_id} // Assuming stage object has stage_id
                        button
                        selected={selectedStageId === stage.stage_id}
                        onClick={() => handleStageClick(stage.stage_id)}
                        secondaryAction={
                            <IconButton
                                edge="end"
                                aria-label="edit"
                                onClick={(e) => handleEditStage(stage.stage_id, e)}
                            >
                                <EditIcon />
                            </IconButton>
                        }
                    >
                        {/* Assuming stage object has stage_name and description */}
                        <ListItemText
                            primary={stage.stage_name || 'Unnamed Stage'}
                            secondary={stage.description || 'No description'}
                        />
                    </ListItem>
                ))}
            </List>
        );
    } else {
        content = <Typography variant="body2" sx={{ p: 2, textAlign: 'center' }}>No stages found for this agent.</Typography>;
    }

    return (
        <Card sx={{ mt: 2 }}>
             <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" gutterBottom component="div">
                        Stages
                    </Typography>
                     {/* Conditionally render Create button only if an agent is selected */}
                     {selectedAgentId && (
                        <Button
                            variant="contained"
                            size="small"
                            startIcon={<AddCircleOutlineIcon />}
                            onClick={handleCreateStage}
                            disabled={!selectedAgentId} // Disable if no agent selected (redundant due to outer check, but safe)
                        >
                            Create Stage
                        </Button>
                     )}
                </Box>
                <Divider sx={{ mb: 1 }}/>
                {content}
            </CardContent>
        </Card>
    );
}

export default StageSection;