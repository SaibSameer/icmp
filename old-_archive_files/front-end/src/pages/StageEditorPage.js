import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Breadcrumbs, 
  Link, 
  Container,
  CircularProgress,
  Alert
} from '@mui/material';
import AddEditStageForm from '../components/AddEditStageForm/AddEditStageForm';
import { getStoredCredentials } from '../utils/authUtils';

const StageEditorPage = () => {
  const { stageId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stageName, setStageName] = useState('');
  
  // Get stored credentials
  const { businessId, businessApiKey } = getStoredCredentials();
  
  useEffect(() => {
    // Check if we have the required credentials
    if (!businessId || !businessApiKey) {
      setError('Authentication required. Please log in.');
      setLoading(false);
      return;
    }
    
    // If we're creating a new stage, no need to fetch stage data
    if (stageId === 'new') {
      setLoading(false);
      return;
    }
    
    // Fetch stage data to get the name for the breadcrumb
    const fetchStageData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/stages/${stageId}?business_id=${businessId}`, {
          headers: {
            'Authorization': `Bearer ${businessApiKey}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stage: ${response.status}`);
        }
        
        const data = await response.json();
        setStageName(data.stage_name || 'Unnamed Stage');
      } catch (err) {
        console.error('Error fetching stage:', err);
        setError(`Failed to load stage: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStageData();
  }, [stageId, businessId, businessApiKey]);
  
  const handleNavigateBack = () => {
    navigate('/stage-management');
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Box sx={{ mt: 2 }}>
          <Link component="button" variant="body1" onClick={handleNavigateBack}>
            Return to Stage Management
          </Link>
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link 
            component="button" 
            variant="body1" 
            onClick={handleNavigateBack}
            color="inherit"
            underline="hover"
          >
            Stage Management
          </Link>
          <Typography color="text.primary">
            {stageId === 'new' ? 'Create New Stage' : stageName}
          </Typography>
        </Breadcrumbs>
        
        <Typography variant="h4" component="h1" gutterBottom>
          {stageId === 'new' ? 'Create New Stage' : `Edit Stage: ${stageName}`}
        </Typography>
      </Paper>
      
      <AddEditStageForm />
    </Container>
  );
};

export default StageEditorPage;