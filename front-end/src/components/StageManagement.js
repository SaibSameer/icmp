import React from 'react';
import {
    TextField, Button, Typography, Card, CardContent, Box,
} from '@mui/material';

function StageManagement({
    stageId,
    setStageId,
    stageName,
    setStageName,
    stageDescription,
    setStageDescription,
    stageType,
    setStageType,
    selectionTemplateId,
    setSelectionTemplateId,
    selectionCustomPrompt,
    setSelectionCustomPrompt,
    extractionTemplateId,
    setExtractionTemplateId,
    extractionCustomPrompt,
    setExtractionCustomPrompt,
    responseTemplateId,
    setResponseTemplateId,
    responseCustomPrompt,
    setResponseCustomPrompt,
    stageOutput,
    setStageOutput,
    fetchStages,
    createStage,
    handleSnackbarOpen,
    businessId
}) {

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Stage Management</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextField label="Stage ID" variant="outlined" value={stageId} onChange={(e) => setStageId(e.target.value)} />
                    <TextField label="Stage Name" variant="outlined" value={stageName} onChange={(e) => setStageName(e.target.value)} />
                    <TextField label="Stage Description" variant="outlined" value={stageDescription} onChange={(e) => setStageDescription(e.target.value)} />
                    <TextField label="Stage Type" variant="outlined" value={stageType} onChange={(e) => setStageType(e.target.value)} />
                    <TextField label="Selection Template ID" variant="outlined" value={selectionTemplateId} onChange={(e) => setSelectionTemplateId(e.target.value)} />
                    <TextField label="Selection Custom Prompt" variant="outlined" value={selectionCustomPrompt} onChange={(e) => setSelectionCustomPrompt(e.target.value)} />
                     <TextField label="Extraction Template ID" variant="outlined" value={extractionTemplateId} onChange={(e) => setExtractionTemplateId(e.target.value)} />
                     <TextField label="Extraction Custom Prompt" variant="outlined" value={extractionCustomPrompt} onChange={(e) => setExtractionCustomPrompt(e.target.value)} />
                    <TextField label="Response Template ID" variant="outlined" value={responseTemplateId} onChange={(e) => setResponseTemplateId(e.target.value)} />
                     <TextField label="Response Custom Prompt" variant="outlined" value={responseCustomPrompt} onChange={(e) => setResponseCustomPrompt(e.target.value)} />
                    <Button variant="contained" onClick={fetchStages}>Fetch Stages</Button>
                    <Button variant="contained" onClick={createStage}>Create Stage</Button>
                    <Typography variant="body1">{stageOutput}</Typography>
                </Box>
            </CardContent>
        </Card>
    );
}

export default StageManagement;