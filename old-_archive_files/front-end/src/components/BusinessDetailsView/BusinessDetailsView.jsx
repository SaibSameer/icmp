import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import AgentSection from '../AgentSection';
import { 
  Snackbar, 
  Alert, 
  Box, 
  IconButton, 
  Typography, 
  Container, 
  Paper,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import DescriptionIcon from '@mui/icons-material/Description';
import LogoutIcon from '@mui/icons-material/Logout';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

// Import services FIRST
import {
    getBusiness, 
    updateBusiness, 
    setDefaultStage 
} from '../../services/businessService'; 

import { 
    fetchStages 
} from '../../services/stageService';

import {
    fetchAgents, 
    createAgent, 
    updateAgent, 
    deleteAgent 
} from '../../services/agentService'; 

// Define your backend API base URL AFTER imports
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function BusinessDetailsView() {
  const navigate = useNavigate();
  const [businessData, setBusinessData] = useState(null);
  const [editFormData, setEditFormData] = useState({}); // State for form data
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false); // Added saving state
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [isEditingAgent, setIsEditingAgent] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [newAgentData, setNewAgentData] = useState({
    agent_name: '',
    agent_description: ''
  });

  // State for default stage selection
  const [availableStages, setAvailableStages] = useState([]); 
  const [selectedStageId, setSelectedStageId] = useState(''); 

  // Get the business ID from localStorage instead of hardcoding
  const businessId = localStorage.getItem('businessId');

  const handleSnackbarOpen = useCallback((message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  }, []);

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleNavigateToLogin = () => {
    navigate('/login');
  };

  const handleLogout = useCallback(() => {
    // Clear localStorage
    localStorage.removeItem('userId');
    localStorage.removeItem('businessId');
    localStorage.removeItem('businessApiKey');
    
    // Show logout message
    handleSnackbarOpen('Logged out successfully', 'success');
    
    // Navigate to login page
    navigate('/login');
  }, [navigate, handleSnackbarOpen]);

  // Navigate to stage management for a specific agent
  const navigateToStageManagement = useCallback((agentId, agentName) => {
    console.log(`Navigating to stages for agent: ${agentName} (${agentId})`);
    
    // Store agent ID in localStorage for persistence
    localStorage.setItem('agentId', agentId);
    
    // Navigate to stages with proper URL format
    navigate(`/stages?business_id=${businessId}&agent_id=${agentId}`);
  }, [navigate, businessId]);

  // Fetch business data, stages, and agents
  const fetchData = useCallback(async () => {
    if (!businessId) {
      setError("Business ID not found. Please login again.");
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null); // Clear previous errors
    console.log(`Fetching data for business ID: ${businessId}`);

    try {
      // Fetch Business Details (ensure service includes first_stage_id)
      // Use await Promise.all for concurrent fetching
      const [fetchedBusinessData, fetchedStages, fetchedAgents] = await Promise.all([
        getBusiness(businessId),
        fetchStages(businessId),
        fetchAgents(businessId)
      ]);

      console.log('Fetched business data:', fetchedBusinessData);
      setBusinessData(fetchedBusinessData);
      setEditFormData(fetchedBusinessData); // Initialize form data with current values
      setSelectedStageId(fetchedBusinessData.first_stage_id || ''); // Set initial dropdown value
      
      console.log('Fetched stages:', fetchedStages);
      setAvailableStages(fetchedStages || []);

      console.log('Fetched agents:', fetchedAgents);
      setAgents(fetchedAgents || []);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(`Failed to load data: ${err.message}`);
      handleSnackbarOpen(`Error loading data: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [businessId, handleSnackbarOpen]);

  useEffect(() => {
    fetchData();
  }, [fetchData]); // Run fetchData when component mounts or fetchData changes

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleEditToggle = () => {
    if (!isEditing && businessData) {
      setEditFormData({
        business_name: businessData.business_name || '',
        business_description: businessData.business_description || '',
        address: businessData.address || '',
        phone_number: businessData.phone_number || '',
        website: businessData.website || ''
      });
    }
    setIsEditing(!isEditing);
    setError(null); // Clear errors when toggling mode
  };

  const handleSaveChanges = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setIsSaving(true); // Indicate saving process
    setError(null);
    console.log("Saving business changes:", editFormData);

    try {
      // Extract only updatable fields
      const dataToUpdate = { 
        business_name: editFormData.business_name, 
        business_description: editFormData.business_description,
        address: editFormData.address,
        phone_number: editFormData.phone_number,
        website: editFormData.website
      }; 
      await updateBusiness(businessId, dataToUpdate);

      // Update the main business data state after successful save
      setBusinessData(prev => ({ ...prev, ...dataToUpdate })); 
      setIsEditing(false); // Exit edit mode
      handleSnackbarOpen('Business details updated successfully!', 'success');
    } catch (err) {
      console.error('Error saving business details:', err);
      setError(`Save failed: ${err.message}`);
      handleSnackbarOpen(`Error saving details: ${err.message}`, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // --- Default Stage Logic ---
  const handleStageSelectChange = (event) => {
    setSelectedStageId(event.target.value);
  };

  const handleSaveDefaultStage = async () => {
    if (!businessId) return;
    setIsSaving(true);
    setError(null);
    try {
      const stageIdToSave = selectedStageId === '' ? null : selectedStageId;
      await setDefaultStage(businessId, stageIdToSave);
      // Update local state optimistically or refetch
      setBusinessData(prev => ({ ...prev, first_stage_id: stageIdToSave })); 
      handleSnackbarOpen('Default starting stage updated successfully!', 'success');
    } catch (err) {
      console.error('Error saving default stage:', err);
      setError(`Failed to save default stage: ${err.message}`);
      handleSnackbarOpen(`Error saving default stage: ${err.message}`, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // Handle edit agent
  const handleEditAgent = (agent) => {
    setEditingAgent(agent);
    setIsEditingAgent(true);
  };

  // Handle delete agent
  const handleDeleteAgent = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) {
      return;
    }
    
    setIsLoading(true);
    try {
      await deleteAgent(businessId, agentId);
      setAgents(prev => prev.filter(agent => agent.agent_id !== agentId));
      handleSnackbarOpen('Agent deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting agent:', error);
      handleSnackbarOpen(`Error deleting agent: ${error.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentDialogClose = () => {
    setIsEditingAgent(false);
    setEditingAgent(null);
    setNewAgentData({ agent_name: '', agent_description: '' }); // Reset form
  };

  const handleAgentFormChange = (event) => {
    const { name, value } = event.target;
    if (editingAgent) {
      setEditingAgent(prev => ({ ...prev, [name]: value }));
    } else {
      setNewAgentData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleAgentFormSubmit = async (event) => {
    event.preventDefault();
    const agentData = editingAgent || newAgentData;
    if (!agentData.agent_name?.trim()) {
      handleSnackbarOpen('Agent name cannot be empty', 'warning');
      return;
    }

    setIsSaving(true); // Use general saving indicator
    try {
      let savedAgent;
      if (editingAgent) {
        savedAgent = await updateAgent(editingAgent.agent_id, agentData);
        setAgents(prev => prev.map(a => a.agent_id === savedAgent.agent_id ? savedAgent : a));
      } else {
        savedAgent = await createAgent(agentData);
        setAgents(prev => [...prev, savedAgent]);
      }
      handleSnackbarOpen(editingAgent ? 'Agent updated' : 'Agent created', 'success');
      handleAgentDialogClose();
    } catch (error) {
      console.error('Error saving agent:', error);
      handleSnackbarOpen(`Error saving agent: ${error.message}`, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <Container><Box display="flex" justifyContent="center" mt={5}><CircularProgress /></Box></Container>;
  }

  // Show login prompt if no businessId (e.g., localStorage cleared)
  if (!businessId) {
    return (
      <Container>
        <Alert severity="warning" sx={{ mt: 2 }}>
          Business ID not found. Please log in or configure your application.
        </Alert>
        <Button onClick={() => navigate('/login')} sx={{ mt: 1 }}>Go to Login</Button>
      </Container>
    );
  }

  // Show error if data fetching failed (and not just loading)
  if (error && !businessData) { // Only show main error if data failed completely
    return <Container><Alert severity="error" sx={{ mt: 2 }}>{error}</Alert></Container>;
  }

  // Should ideally not happen if businessId exists, but good fallback
  if (!businessData) { 
    return <Container><Alert severity="info" sx={{ mt: 2 }}>No business data loaded.</Alert></Container>;
  }

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <IconButton onClick={() => navigate(-1)}> {/* Go back */} 
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Business Dashboard
          </Typography>
          <Button 
            variant="outlined" 
            startIcon={<LogoutIcon />} 
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Box>

        {/* Display any general saving error */} 
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* --- Business Details Section --- */} 
        <Box mb={4}>
          <Typography variant="h5" gutterBottom>Business Details</Typography>
          {!isEditing ? (
            <Box>
              <Typography><strong>Name:</strong> {businessData.business_name}</Typography>
              <Typography><strong>Description:</strong> {businessData.business_description || 'N/A'}</Typography>
              <Typography><strong>Address:</strong> {businessData.address || 'N/A'}</Typography>
              <Typography><strong>Phone:</strong> {businessData.phone_number || 'N/A'}</Typography>
              <Typography><strong>Website:</strong> {businessData.website ? <a href={businessData.website} target="_blank" rel="noopener noreferrer">{businessData.website}</a> : 'N/A'}</Typography>
              <Typography><strong>Business ID:</strong> {businessData.business_id}</Typography>
              <Typography><strong>Owner ID:</strong> {businessData.owner_id}</Typography>
              <Button 
                variant="contained" 
                startIcon={<EditIcon />} 
                onClick={handleEditToggle} 
                sx={{ mt: 2 }}
              >
                Edit Details
              </Button>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleSaveChanges} noValidate autoComplete="off">
              <TextField 
                label="Business Name"
                name="business_name"
                value={editFormData.business_name || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                required
                disabled={isSaving}
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
                disabled={isSaving}
              />
              <TextField 
                label="Address"
                name="address"
                value={editFormData.address || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                disabled={isSaving}
              />
              <TextField 
                label="Phone Number"
                name="phone_number"
                value={editFormData.phone_number || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                disabled={isSaving}
              />
              <TextField 
                label="Website"
                name="website"
                value={editFormData.website || ''}
                onChange={handleInputChange}
                fullWidth 
                margin="normal"
                type="url"
                disabled={isSaving}
              />
              <Box sx={{ mt: 2 }}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  disabled={isSaving}
                  sx={{ mr: 1 }}
                >
                  {isSaving ? <CircularProgress size={24} /> : 'Save Changes'}
                </Button>
                <Button variant="outlined" onClick={handleEditToggle} disabled={isSaving}>
                  Cancel
                </Button>
              </Box>
            </Box>
          )}
        </Box>

        <hr />

        {/* --- Default Stage Selection Section --- */} 
        <Box mt={4} mb={4}>
          <Typography variant="h6" gutterBottom>Conversation Settings</Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel id="default-stage-label">Default Starting Stage</InputLabel>
            <Select
              labelId="default-stage-label"
              id="default-stage-select"
              value={selectedStageId} // Bind to state
              label="Default Starting Stage"
              onChange={handleStageSelectChange} // Handle change
              disabled={isSaving || isLoading} // Disable while loading/saving
            >
              {/* "None" option */}
              <MenuItem value="">
                <em>None (System will pick first available)</em>
              </MenuItem>
              {/* Map available stages */} 
              {availableStages.length > 0 ? (
                availableStages.map((stage) => {
                  // --- DEBUGGING LOG --- 
                  console.log("Rendering stage:", stage);
                  // ---------------------
                  
                  // Find the agent name using the stage's agent_id
                  // Ensure agents state is populated before trying to find
                  const linkedAgent = agents && agents.find(agent => agent.agent_id === stage.agent_id);
                  const agentNameDisplay = linkedAgent ? ` (Agent: ${linkedAgent.agent_name})` : ''; // Display agent name if found
                  const displayText = `${stage.stage_name}${agentNameDisplay}`;

                  // --- DEBUGGING LOG --- 
                  console.log("Display text:", displayText);
                  // ---------------------
                  
                  return (
                    <MenuItem key={stage.stage_id} value={stage.stage_id}>
                      {/* Display Stage Name and potentially Agent Name */} 
                      {displayText}
                    </MenuItem>
                  );
                })
              ) : (
                <MenuItem disabled>No stages available for this business</MenuItem>
              )}
            </Select>
          </FormControl>
          <Button 
            variant="contained" 
            onClick={handleSaveDefaultStage} // Save handler
            disabled={isSaving || isLoading || selectedStageId === (businessData.first_stage_id || '')} // Disable if no change
            sx={{ mt: 2 }}
          >
            {isSaving ? <CircularProgress size={24} /> : 'Save Default Stage'}
          </Button>
        </Box>
        
        <hr />

        {/* --- Agent Section --- */} 
        {/* Pass necessary props and handlers to AgentSection */}
        <AgentSection 
          agents={agents}
          isLoading={isLoading} // Pass loading state if needed by AgentSection
          isSaving={isSaving} // Pass saving state
          businessId={businessId}
          onEditAgent={handleEditAgent} 
          onDeleteAgent={handleDeleteAgent}
          onNavigateToStages={navigateToStageManagement} 
          onAddAgent={() => { setEditingAgent(null); setIsEditingAgent(true); }} // Open dialog for new agent
          handleSnackbarOpen={handleSnackbarOpen} // Pass snackbar handler
        />

        {/* --- Dialog for Adding/Editing Agent --- */} 
        <Dialog open={isEditingAgent} onClose={handleAgentDialogClose} fullWidth maxWidth="sm">
          <DialogTitle>{editingAgent ? 'Edit Agent' : 'Add New Agent'}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="agent_name"
              label="Agent Name"
              type="text"
              fullWidth
              variant="standard"
              value={editingAgent ? editingAgent.agent_name : newAgentData.agent_name}
              onChange={handleAgentFormChange}
              required
              disabled={isSaving}
            />
            <TextField
              margin="dense"
              name="agent_description"
              label="Agent Description"
              type="text"
              fullWidth
              variant="standard"
              multiline
              rows={3}
              value={editingAgent ? editingAgent.agent_description : newAgentData.agent_description}
              onChange={handleAgentFormChange}
              disabled={isSaving}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleAgentDialogClose} disabled={isSaving}>Cancel</Button>
            <Button 
              onClick={handleAgentFormSubmit} 
              variant="contained" 
              disabled={isSaving || !(editingAgent || newAgentData).agent_name?.trim()} // Disable if name empty
            >
              {isSaving ? <CircularProgress size={24} /> : (editingAgent ? 'Save Changes' : 'Create Agent')}
            </Button>
          </DialogActions>
        </Dialog>

      </Paper>

      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

    </Container>
  );
}

export default BusinessDetailsView;