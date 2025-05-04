import React, { useEffect, useState, useCallback } from 'react';
import { API_BASE_URL } from '../config';
import { 
    Box, Typography, TextField, Button, CircularProgress, Alert, 
    Select, MenuItem, FormControl, InputLabel, Dialog, DialogTitle, DialogContent
} from '@mui/material';
import { businessService } from '../services/businessService';
import { stageService } from '../services/stageService';
import MessagePortal from './MessagePortal';
import MessageIcon from '@mui/icons-material/Message';

const BusinessDetailsView = () => {
  const [businessId, setBusinessId] = useState(localStorage.getItem('businessId'));
  const [businessData, setBusinessData] = useState(null);
  const [editFormData, setEditFormData] = useState(null);
  const [availableStages, setAvailableStages] = useState([]);
  const [selectedStageId, setSelectedStageId] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [showMessages, setShowMessages] = useState(false);

  const handleSnackbarOpen = (message, variant) => { console.log(`${variant}: ${message}`); };

  const fetchData = useCallback(async () => {
      if (!businessId) {
          setError("Please login and configure your business to view details.");
          setIsLoading(false);
          return;
      }
      setIsLoading(true);
      setError(null);
      console.log(`Fetching data for business ID: ${businessId}`);

      try {
          const fetchedBusinessData = await businessService.getBusiness(businessId);
          console.log('Fetched business data:', fetchedBusinessData);
          setBusinessData(fetchedBusinessData);
          setEditFormData(fetchedBusinessData); 
          setSelectedStageId(fetchedBusinessData.first_stage_id || '');
          
          const fetchedStages = await stageService.getStages(businessId);
          console.log('Fetched stages:', fetchedStages);
          setAvailableStages(fetchedStages || []);
          
      } catch (err) {
          console.error('Error fetching data:', err);
          setError(err.message);
      } finally {
          setIsLoading(false);
      }
  }, [businessId]);

  useEffect(() => {
      fetchData();
  }, [fetchData]);

  const handleStageSelectChange = (event) => {
      setSelectedStageId(event.target.value);
  };

  const handleSaveDefaultStage = async () => {
      if (!businessId) return;
      setIsSaving(true);
      setError(null);
      try {
          const stageIdToSave = selectedStageId === '' ? null : selectedStageId;
          await businessService.setDefaultStage(businessId, stageIdToSave);
          handleSnackbarOpen('Default starting stage updated successfully!', 'success');
      } catch (err) {
          console.error('Error saving default stage:', err);
          setError(err.message);
          handleSnackbarOpen(`Error saving default stage: ${err.message}`, 'error');
      } finally {
          setIsSaving(false);
      }
  };

  const handleInputChange = (event) => {
      const { name, value } = event.target;
      setEditFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveDetails = async () => {
      if (!businessId || !editFormData) return;
      setIsSaving(true);
      setError(null);
      try {
          const dataToUpdate = { 
              business_name: editFormData.business_name, 
              business_description: editFormData.business_description,
              address: editFormData.address,
              phone_number: editFormData.phone_number,
              website: editFormData.website
          }; 
          await businessService.updateBusiness(businessId, dataToUpdate);
          handleSnackbarOpen('Business details updated successfully!', 'success');
          setBusinessData(prev => ({ ...prev, ...dataToUpdate })); 
      } catch (err) {
          console.error('Error updating business details:', err);
          setError(err.message);
          handleSnackbarOpen(`Error updating details: ${err.message}`, 'error');
      } finally {
          setIsSaving(false);
      }
  };

  if (isLoading) {
    return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;
  }

  if (error) {
    return <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>;
  }

  if (!businessData || !editFormData) {
    return <Alert severity="warning" sx={{ mt: 2 }}>No business data found. Please configure first.</Alert>;
  }

  return (
    <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Business Details</Typography>
            <Button
                variant="contained"
                startIcon={<MessageIcon />}
                onClick={() => setShowMessages(true)}
            >
                View Messages
            </Button>
        </Box>
        
        <Box component="form" noValidate autoComplete="off" sx={{ mb: 4 }}>
            <TextField 
                label="Business Name"
                name="business_name"
                value={editFormData.business_name || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                required
            />
            <TextField 
                label="Description"
                name="business_description"
                value={editFormData.business_description || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                multiline
                rows={3}
            />
             <TextField 
                label="Address"
                name="address"
                value={editFormData.address || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
            />
             <TextField 
                label="Phone Number"
                name="phone_number"
                value={editFormData.phone_number || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
            />
             <TextField 
                label="Website"
                name="website"
                value={editFormData.website || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
            />
            <Button 
                variant="contained" 
                onClick={handleSaveDetails}
                disabled={isSaving}
                sx={{ mt: 2 }}
            >
                {isSaving ? <CircularProgress size={24} /> : 'Save Details'}
            </Button>
        </Box>

        <hr />

        <Box sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h6" gutterBottom>Conversation Settings</Typography>
            <FormControl fullWidth margin="normal">
                <InputLabel id="default-stage-label">Default Starting Stage</InputLabel>
                <Select
                    labelId="default-stage-label"
                    id="default-stage-select"
                    value={selectedStageId}
                    label="Default Starting Stage"
                    onChange={handleStageSelectChange}
                >
                    <MenuItem value=""><em>None (System Default)</em></MenuItem>
                    {availableStages.map((stage) => (
                        <MenuItem key={stage.stage_id} value={stage.stage_id}>
                            {stage.stage_name} ({stage.stage_id.substring(0, 8)}...)
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Button 
                variant="contained" 
                onClick={handleSaveDefaultStage}
                disabled={isSaving}
                sx={{ mt: 2 }}
            >
                {isSaving ? <CircularProgress size={24} /> : 'Save Default Stage'}
            </Button>
        </Box>

        <Dialog
            open={showMessages}
            onClose={() => setShowMessages(false)}
            maxWidth="lg"
            fullWidth
        >
            <DialogTitle>Business Messages</DialogTitle>
            <DialogContent>
                <MessagePortal />
            </DialogContent>
        </Dialog>
    </Box>
  );
};

export default BusinessDetailsView;