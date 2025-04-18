import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import AddEditStageForm from './AddEditStageForm/AddEditStageForm';

const StageEditor = ({ stageId }) => {
  const navigate = useNavigate();
  
  // State variables
  const [stage, setStage] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Get stored credentials
  const getStoredCredentials = () => {
    return {
      businessId: localStorage.getItem('businessId') || '',
      businessApiKey: localStorage.getItem('businessApiKey') || ''
    };
  };

  // Track if component is mounted
  const isMounted = useRef(true);
  
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Fetch stage data on component mount
  useEffect(() => {
    const { businessId, businessApiKey } = getStoredCredentials();
    
    if (!businessId || !businessApiKey) {
      setError('Authentication required. Please log in.');
      return;
    }
    
    if (stageId && stageId !== 'new') {
      fetchStage(stageId, businessId, businessApiKey);
    }
  }, [stageId]);
  
  // Fetch specific stage data
  const fetchStage = async (id, businessId, businessApiKey) => {
    if (!isMounted.current || !businessId || !businessApiKey) {
      console.error('Missing required parameters:', { id, businessId, hasApiKey: !!businessApiKey });
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      params.append('business_id', businessId);
      
      const url = `/stages/${id}?${params.toString()}`;
      console.log('Fetching stage from URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${businessApiKey}`
        },
        credentials: 'include'
      });
      
      console.log('Response status:', response.status);
      
      // Log the raw response text first
      const responseText = await response.text();
      console.log('Raw response text:', responseText);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch stage: ${response.status} ${responseText || ''}`);
      }
      
      // Try to parse the response text as JSON
      let data;
      try {
        data = JSON.parse(responseText);
        console.log('Parsed stage data:', data);
      } catch (parseError) {
        console.error('Failed to parse response as JSON:', parseError);
        throw new Error('Invalid JSON response from server');
      }
      
      if (!data) {
        throw new Error('Empty response from server');
      }

      // Validate required fields
      const requiredFields = ['stage_name', 'stage_description', 'stage_type'];
      const missingFields = requiredFields.filter(field => !data[field]);
      if (missingFields.length > 0) {
        console.error('Missing required fields:', missingFields);
        console.log('Available fields:', Object.keys(data));
        throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
      }
      
      if (isMounted.current) {
        setStage(data);
        setError('');
        console.log('Stage state set to:', data);
      }
    } catch (err) {
      console.error('Error in fetchStage:', err);
      if (isMounted.current) {
        setError(`Error: ${err.message}`);
        setStage(null);
      }
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  };
  
  // Handle return to stage management
  const handleReturn = () => {
    navigate('/stage-management');
  };
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          variant="outlined"
          onClick={handleReturn}
          sx={{ mt: 2 }}
        >
          Return to Stage Management
        </Button>
      </Box>
    );
  }
  
  if (!stage) {
    return (
      <Box>
        <Alert severity="info" sx={{ mb: 2 }}>
          No stage data available. This could mean either:
          <ul>
            <li>The stage doesn't exist</li>
            <li>The data format is invalid</li>
            <li>There was an error fetching the data</li>
          </ul>
          {error && <Typography color="error">Error details: {error}</Typography>}
        </Alert>
        <Button 
          variant="outlined"
          onClick={handleReturn}
          sx={{ mt: 2 }}
        >
          Return to Stage Management
        </Button>
      </Box>
    );
  }
  
  // Add debug output before render
  console.log('Rendering stage:', stage);

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {stageId === 'new' ? 'Create New Stage' : 'Edit Stage'}
        </Typography>
        
        <AddEditStageForm stageId={stageId} />
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-start' }}>
          <Button
            variant="outlined"
            onClick={handleReturn}
            sx={{ mr: 2 }}
          >
            Return to Stage Management
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default StageEditor;