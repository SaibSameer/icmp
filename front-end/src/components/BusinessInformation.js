import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { API_CONFIG } from '../config';

function BusinessInformation() {
  const { businessId } = useParams();
  const navigate = useNavigate();
  const [businessData, setBusinessData] = useState(null);
  const [businessInfo, setBusinessInfo] = useState('');
  const [editableInfo, setEditableInfo] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(null);
  const [updateError, setUpdateError] = useState(null);

  const adminApiKey = sessionStorage.getItem('adminApiKey');

  useEffect(() => {
    fetchBusinessInformation();
  }, [businessId]);

  const fetchBusinessInformation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/${businessId}`, {
        headers: {
          'Authorization': `Bearer ${adminApiKey}`,
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch business information');
      }

      const data = await response.json();
      setBusinessData(data);
      setBusinessInfo(data.business_information || '');
      setEditableInfo(data.business_information || '');
    } catch (err) {
      console.error('Error fetching business information:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = () => {
    setIsEditing(true);
    setUpdateSuccess(null);
    setUpdateError(null);
  };

  const handleCancelClick = () => {
    setEditableInfo(businessInfo);
    setIsEditing(false);
    setUpdateError(null);
  };

  const handleSaveClick = async () => {
    setUpdateSuccess(null);
    setUpdateError(null);
    try {
      // Create a complete business data object with all required fields
      const updatedBusinessData = {
        ...businessData,
        business_information: editableInfo
      };

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/businesses/${businessId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${adminApiKey}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(updatedBusinessData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update business information');
      }

      // Even if response is ok, try to parse the response data
      try {
        const updatedData = await response.json();
        setBusinessData(updatedData);
        setBusinessInfo(updatedData.business_information || '');
        setEditableInfo(updatedData.business_information || '');
      } catch (parseError) {
        // If we can't parse the response, just use the current data
        setBusinessInfo(editableInfo);
        setEditableInfo(editableInfo);
      }

      setIsEditing(false);
      setUpdateSuccess('Business information updated successfully!');
    } catch (err) {
      console.error('Error updating business information:', err);
      setUpdateError(err.message);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Business Information</Typography>
          {!isEditing ? (
            <Button variant="contained" onClick={handleEditClick}>
              Edit Information
            </Button>
          ) : (
            <Box>
              <Button variant="outlined" onClick={handleCancelClick} sx={{ mr: 2 }}>
                Cancel
              </Button>
              <Button variant="contained" onClick={handleSaveClick}>
                Save Changes
              </Button>
            </Box>
          )}
        </Box>

        {updateSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {updateSuccess}
          </Alert>
        )}

        {updateError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {updateError}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12}>
            {isEditing ? (
              <TextField
                fullWidth
                multiline
                rows={10}
                variant="outlined"
                value={editableInfo}
                onChange={(e) => setEditableInfo(e.target.value)}
                label="Business Information"
              />
            ) : (
              <Paper variant="outlined" sx={{ p: 2, minHeight: 200 }}>
                <Typography whiteSpace="pre-wrap">
                  {businessInfo || 'No business information available.'}
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

export default BusinessInformation;