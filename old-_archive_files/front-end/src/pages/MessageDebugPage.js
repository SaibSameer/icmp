import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Paper, Typography, Grid, CircularProgress, Divider } from '@mui/material';
import { debugService } from '../services/debugService';

// Component to display prompt details
const PromptDisplay = ({ title, prompt, response }) => (
    <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>{title}</Typography>
        <Box sx={{ bgcolor: 'grey.100', p: 2, mb: 2, borderRadius: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">Prompt:</Typography>
            <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {prompt}
            </Typography>
        </Box>
        <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">Response:</Typography>
            <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {response}
            </Typography>
        </Box>
    </Paper>
);

// Component to display stage navigation
const StageNavigation = ({ stages }) => (
    <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>Stage Navigation</Typography>
        <Box sx={{ display: 'flex', overflowX: 'auto', pb: 1 }}>
            {stages.map((stage, index) => (
                <React.Fragment key={stage.id}>
                    <Box sx={{ 
                        p: 1, 
                        bgcolor: stage.current ? 'primary.main' : 'grey.100',
                        color: stage.current ? 'white' : 'text.primary',
                        borderRadius: 1,
                        minWidth: 'fit-content'
                    }}>
                        <Typography variant="body2">{stage.name}</Typography>
                        <Typography variant="caption" display="block">
                            Confidence: {stage.confidence}
                        </Typography>
                    </Box>
                    {index < stages.length - 1 && (
                        <Box sx={{ display: 'flex', alignItems: 'center', px: 1 }}>→</Box>
                    )}
                </React.Fragment>
            ))}
        </Box>
    </Paper>
);

// Component to display extracted data
const DataExtraction = ({ data }) => (
    <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>Extracted Data</Typography>
        <Box component="pre" sx={{ 
            bgcolor: 'grey.100', 
            p: 2, 
            borderRadius: 1,
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace'
        }}>
            {JSON.stringify(data, null, 2)}
        </Box>
    </Paper>
);

// Main debug page component
const MessageDebugPage = () => {
    const { conversationId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [debugData, setDebugData] = useState(null);
    const [realTimeEvents, setRealTimeEvents] = useState([]);

    useEffect(() => {
        const loadDebugData = async () => {
            try {
                const data = await debugService.getConversationDebug(conversationId);
                setDebugData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        // Subscribe to real-time events
        const cleanup = debugService.subscribeToDebugEvents(conversationId, (event) => {
            setRealTimeEvents(prev => [...prev, event]);
        });

        loadDebugData();
        return cleanup; // Cleanup subscription on unmount
    }, [conversationId]);

    if (loading) return <CircularProgress />;
    if (error) return <Typography color="error">{error}</Typography>;
    if (!debugData) return <Typography>No debug data available</Typography>;

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Message Processing Debug View
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
                Conversation ID: {conversationId}
            </Typography>
            
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <StageNavigation stages={debugData.stages} />
                </Grid>

                <Grid item xs={12}>
                    <PromptDisplay 
                        title="Stage Selection"
                        prompt={debugData.stageSelection.prompt}
                        response={debugData.stageSelection.response}
                    />
                </Grid>

                <Grid item xs={12}>
                    <PromptDisplay 
                        title="Data Extraction"
                        prompt={debugData.dataExtraction.prompt}
                        response={debugData.dataExtraction.response}
                    />
                </Grid>

                <Grid item xs={12}>
                    <DataExtraction data={debugData.extractedData} />
                </Grid>

                <Grid item xs={12}>
                    <PromptDisplay 
                        title="Response Generation"
                        prompt={debugData.responseGeneration.prompt}
                        response={debugData.responseGeneration.response}
                    />
                </Grid>

                {realTimeEvents.length > 0 && (
                    <Grid item xs={12}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>Real-time Events</Typography>
                            <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                                {realTimeEvents.map((event, index) => (
                                    <Box key={index} sx={{ mb: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            {new Date(event.timestamp).toLocaleTimeString()}
                                        </Typography>
                                        <Typography>{event.message}</Typography>
                                        <Divider sx={{ my: 1 }} />
                                    </Box>
                                ))}
                            </Box>
                        </Paper>
                    </Grid>
                )}
            </Grid>
        </Box>
    );
};

export default MessageDebugPage;