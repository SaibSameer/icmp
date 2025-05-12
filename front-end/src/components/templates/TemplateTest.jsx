import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Paper,
    Container,
    CircularProgress,
    Alert,
    Divider,
    Grid
} from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import templateService from '../../services/templateService';

function TemplateTest() {
    const [searchParams] = useSearchParams();
    const businessId = searchParams.get('businessId');
    const agentId = searchParams.get('agentId');
    
    const [userId, setUserId] = useState('');
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [substitutedContent, setSubstitutedContent] = useState({});
    const [testResults, setTestResults] = useState(null);

    useEffect(() => {
        if (businessId && agentId) {
            fetchTemplates();
        }
    }, [businessId, agentId]);

    const fetchTemplates = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await templateService.getTemplates(businessId, agentId);
            setTemplates(response);
        } catch (err) {
            console.error("Failed to fetch templates:", err);
            setError('Failed to fetch templates. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleTestTemplate = async () => {
        if (!userId) {
            setError('Please enter a user ID');
            return;
        }

        setLoading(true);
        setError('');
        try {
            const result = await templateService.testTemplate(businessId, agentId, {
                user_id: userId,
                template_type: 'response_generation' // For testing, we'll use response generation template
            });
            setTestResults(result);
        } catch (err) {
            console.error("Error testing template:", err);
            setError('Failed to test template. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3 }}>
                <Typography variant="h5" component="h1" gutterBottom>
                    Template Test Page
                </Typography>
                
                <Divider sx={{ mb: 3 }} />

                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            label="User ID"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            placeholder="Enter user ID for testing"
                            helperText="Enter the user ID to test template variable substitution"
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleTestTemplate}
                            disabled={loading || !userId}
                            sx={{ mt: 1 }}
                        >
                            {loading ? <CircularProgress size={24} /> : 'Test Template'}
                        </Button>
                    </Grid>
                </Grid>

                {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        {error}
                    </Alert>
                )}

                {testResults && (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h6" gutterBottom>
                            Test Results
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                            <Typography variant="subtitle1" gutterBottom>
                                Stage Selection Template:
                            </Typography>
                            <Typography variant="body1" component="pre" sx={{ 
                                whiteSpace: 'pre-wrap',
                                bgcolor: 'white',
                                p: 2,
                                borderRadius: 1
                            }}>
                                {testResults.stage_selection?.content || 'No stage selection template found'}
                            </Typography>

                            <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>
                                Data Extraction Template:
                            </Typography>
                            <Typography variant="body1" component="pre" sx={{ 
                                whiteSpace: 'pre-wrap',
                                bgcolor: 'white',
                                p: 2,
                                borderRadius: 1
                            }}>
                                {testResults.data_extraction?.content || 'No data extraction template found'}
                            </Typography>

                            <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>
                                Response Generation Template:
                            </Typography>
                            <Typography variant="body1" component="pre" sx={{ 
                                whiteSpace: 'pre-wrap',
                                bgcolor: 'white',
                                p: 2,
                                borderRadius: 1
                            }}>
                                {testResults.response_generation?.content || 'No response generation template found'}
                            </Typography>
                        </Paper>
                    </Box>
                )}
            </Paper>
        </Container>
    );
}

export default TemplateTest; 