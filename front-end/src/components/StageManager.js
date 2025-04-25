import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Grid,
  Box,
  IconButton,
  Divider,
  Alert,
  Snackbar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Card,
  CardContent,
  FormHelperText,
  ListSubheader
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import DescriptionIcon from '@mui/icons-material/Description';
import VisibilityIcon from '@mui/icons-material/Visibility';
import StarIcon from '@mui/icons-material/Star';
import { fetchStages, createStage, updateStage, deleteStage } from '../services/stageService';
import { getAuthHeaders } from '../services/authService';
import useAgents from '../hooks/useAgents';
import { API_CONFIG } from '../config';

const StageManager = () => {
  // Get parameters from URL and location
  const { businessId: paramBusinessId, agentId: paramAgentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract query parameters if not using path params
  const queryParams = new URLSearchParams(location.search);
  const queryBusinessId = queryParams.get('business_id');
  const queryAgentId = queryParams.get('agent_id');
  
  // Use params or query params, then fallback to localStorage
  const businessId = paramBusinessId || queryBusinessId || localStorage.getItem('businessId');
  const agentId = paramAgentId || queryAgentId || localStorage.getItem('agentId');
  
  // States for stages and templates
  const [stages, setStages] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [stageToDelete, setStageToDelete] = useState(null);
  const [newStageName, setNewStageName] = useState('');
  const [stageDescription, setStageDescription] = useState('');
  const [stageType, setStageType] = useState('conversation');
  const [availableTemplates, setAvailableTemplates] = useState({
    stage_selection: [],
    data_extraction: [],
    response_generation: []
  });
  const [selectedTemplates, setSelectedTemplates] = useState({
    stage_selection: '',
    data_extraction: '',
    response_generation: ''
  });
  const [defaultTemplates, setDefaultTemplates] = useState({
    stage_selection: '',
    data_extraction: '',
    response_generation: ''
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [agentName, setAgentName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { agents, isLoading: agentsLoading, error: agentsError, refreshAgents } = useAgents();
  const [selectedAgentId, setSelectedAgentId] = useState('');

  // Store current values in localStorage for persistence
  useEffect(() => {
    if (businessId) {
      localStorage.setItem('businessId', businessId);
    }
    if (agentId) {
      localStorage.setItem('agentId', agentId);
    }
  }, [businessId, agentId]);

  // Logging for debugging
  useEffect(() => {
    console.log("StageManager - Current params:", { 
      paramBusinessId, 
      paramAgentId,
      queryBusinessId,
      queryAgentId,
      resolvedBusinessId: businessId,
      resolvedAgentId: agentId
    });
  }, [
    paramBusinessId, 
    paramAgentId, 
    queryBusinessId, 
    queryAgentId, 
    businessId, 
    agentId
  ]);

  // Fetch templates for this business
  const fetchTemplates = async () => {
    try {
      const headers = getAuthHeaders();
      
      // Corrected URL: removed /api prefix
      const response = await fetch(`${API_CONFIG.BASE_URL}/templates?business_id=${businessId}`, { 
        headers,
        credentials: 'include'
      });
      
      if (!response.ok) {
        console.error('Template fetch error:', response.status, response.statusText);
        throw new Error('Failed to fetch templates');
      }
      
      const templates = await response.json();
      console.log('Fetched templates:', templates);
      
      // Initialize template categories
      const templatesByType = {
        stage_selection: [],
        data_extraction: [],
        response_generation: []
      };

      // Process and categorize templates
      templates.forEach(template => {
        // Add isDefault flag to identify default templates
        const normalizedTemplate = {
          ...template,
          isDefault: template.template_type.startsWith('default_')
        };

        // Map template types to categories
        const typeMapping = {
          'stage_selection': 'stage_selection',
          'default_stage_selection': 'stage_selection',
          'data_extraction': 'data_extraction',
          'default_data_extraction': 'data_extraction',
          'response_generation': 'response_generation',
          'default_response_generation': 'response_generation'
        };

        const category = typeMapping[template.template_type];
        if (category) {
          templatesByType[category].push(normalizedTemplate);
        }
      });

      // Sort templates within each category
      Object.keys(templatesByType).forEach(category => {
        templatesByType[category].sort((a, b) => {
          // Sort by isDefault first (default templates first)
          if (a.isDefault !== b.isDefault) {
            return a.isDefault ? -1 : 1;
          }
          // Then sort by name
          return a.template_name.localeCompare(b.template_name);
        });
      });

      setAvailableTemplates(templatesByType);
      
      // Set default templates if available
      const defaultTemplates = {
        stage_selection: '',
        data_extraction: '',
        response_generation: ''
      };
      
      // Find default templates in each category
      Object.keys(templatesByType).forEach(category => {
        const defaultTemplate = templatesByType[category].find(t => t.isDefault);
        if (defaultTemplate) {
          defaultTemplates[category] = defaultTemplate.template_id;
        }
      });
      
      setDefaultTemplates(defaultTemplates);
      
      // If we're opening the dialog, pre-select default templates
      if (openDialog) {
        setSelectedTemplates(defaultTemplates);
      }
      
    } catch (error) {
      console.error('Error fetching templates:', error);
      setError('Failed to load templates. Please try again.');
    }
  };

  // Handle template selection change
  const handleTemplateChange = (event, templateType) => {
    const templateId = event.target.value;
    console.log(`Template changed for ${templateType}: ${templateId}`);
    
    setSelectedTemplates(prev => ({
      ...prev,
      [templateType]: templateId
    }));
  };

  // Fetch stages based on business ID and agent ID
  const fetchStagesData = useCallback(async () => {
    if (!businessId) {
      console.error("No business ID available for fetching stages");
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    try {
      console.log("Fetching stages for business:", businessId);
      const stagesData = await fetchStages(businessId);
      console.log("Fetched stages:", stagesData);
      setStages(stagesData);
    } catch (err) {
      console.error("Error fetching stages:", err);
      showSnackbar(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [businessId]);

  // Fetch agent details
  const fetchAgentDetails = useCallback(async () => {
    if (!businessId || !agentId) {
      return;
    }

    try {
      // Construct the correct URL using API_CONFIG
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AGENTS}/${agentId}?business_id=${businessId}`, {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('businessApiKey')}`
        },
        credentials: 'include' // Keep credentials if needed by backend
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch agent details');
      }
      
      const agentData = await response.json();
      setAgentName(agentData.agent_name || `Agent ${agentId}`);
    } catch (err) {
      console.error("Error fetching agent details:", err);
      setAgentName(`Agent ${agentId}`); // Fallback
    }
  }, [businessId, agentId]);

  // Initial data fetch
  useEffect(() => {
    if (businessId) {
      const loadData = async () => {
        setIsLoading(true);
        setError('');
        
        try {
          // Load templates first
          await fetchTemplates();
          // Then load stages
          await fetchStagesData();
          
          // Set the selected agent ID if it exists in the stage data
          if (selectedStage && selectedStage.agent_id) {
            setSelectedAgentId(selectedStage.agent_id);
          } else {
            setSelectedAgentId('');
          }
        } catch (err) {
          console.error("Error in initial data load:", err);
          showSnackbar("Failed to load initial data: " + err.message, 'error');
        } finally {
          setIsLoading(false);
        }
      };
      
      loadData();
    }
  }, [businessId]);

  // Update useEffect to fetch agent details
  useEffect(() => {
    if (agentId) {
      fetchAgentDetails();
    }
  }, [agentId, fetchAgentDetails]);

  // Helper function for showing snackbar messages
  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  const handleNavigateToHome = () => {
    navigate('/business');
  };

  const handleOpenNewStageDialog = () => {
    setNewStageName('');
    setStageDescription('');
    setStageType('conversation');
    
    // Set default templates if available
    setSelectedTemplates(defaultTemplates);
    
    setSelectedAgentId(agentId || ''); // Set the selected agent ID to the current agent ID
    setOpenDialog(true);
  };

  const handleCreateStage = async () => {
    if (!newStageName.trim()) {
      setError('Stage name is required');
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const stageData = {
        business_id: businessId,
        agent_id: selectedAgentId, // Include the selected agent ID
        stage_name: newStageName.trim(),
        stage_description: stageDescription.trim(),
        stage_type: stageType,
        stage_selection_template_id: selectedTemplates.stage_selection || null,
        data_extraction_template_id: selectedTemplates.data_extraction || null,
        response_generation_template_id: selectedTemplates.response_generation || null
      };
      
      console.log('Creating stage with data:', stageData);

      // Use the createStage function from stageService
      const result = await createStage(stageData);
      console.log('Stage created successfully:', result);
      
      showSnackbar('Stage created successfully', 'success');
      
      // Reset form
      setNewStageName('');
      
      // Refresh stages
      fetchStagesData();
      
      // Close dialog
      setOpenDialog(false);
    } catch (error) {
      console.error('Error creating stage:', error);
      showSnackbar(error.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const navigateToStageView = (stageId) => {
    // Construct the URL with query parameters
    let url = `/api/stages/${stageId}?business_id=${businessId}`;
    if (agentId) {
      url += `&agent_id=${agentId}`;
    }
    navigate(url);
  };

  const handleDeleteStage = async () => {
    if (!stageToDelete || !businessId) return;

    try {
      await deleteStage(stageToDelete.stage_id, businessId);
      await fetchStagesData();
      setOpenDeleteDialog(false);
      showSnackbar('Stage deleted successfully', 'success');
    } catch (err) {
      console.error("Error deleting stage:", err);
      showSnackbar(err.message, 'error');
    }
  };

  const handleMoveStage = async (stageId, direction) => {
    try {
      const currentIndex = stages.findIndex(s => s.stage_id === stageId);
      if (currentIndex === -1) return;
      
      // If trying to move first item up or last item down, do nothing
      if ((currentIndex === 0 && direction === 'up') || 
          (currentIndex === stages.length - 1 && direction === 'down')) {
        return;
      }
      
      const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
      
      // Swap the order values in the stage_config
      const updatedStages = [...stages];
      const currentStage = { ...updatedStages[currentIndex] };
      const targetStage = { ...updatedStages[targetIndex] };
      
      // Update stage_config.order values
      currentStage.stage_config = { ...currentStage.stage_config, order: targetIndex + 1 };
      targetStage.stage_config = { ...targetStage.stage_config, order: currentIndex + 1 };
      
      // Update both stages in the database
      const currentUpdate = fetch(`/stages/${currentStage.stage_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(currentStage),
      });
      
      const targetUpdate = fetch(`/stages/${targetStage.stage_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(targetStage),
      });
      
      await Promise.all([currentUpdate, targetUpdate]);
      
      // Refresh stages
      await fetchStagesData();
      showSnackbar('Stage order updated', 'success');
    } catch (err) {
      showSnackbar(err.message, 'error');
    }
  };

  // Add a handler for agent selection
  const handleAgentChange = (event) => {
    setSelectedAgentId(event.target.value);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <IconButton onClick={handleNavigateToHome} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h5" component="h1" gutterBottom sx={{ flexGrow: 1 }}>
            Stage Manager
            {businessId && <Typography variant="subtitle1" component="span" color="text.secondary">
              {` - Business ID: ${businessId}`}
              {agentId && ` - Agent: ${agentName || agentId}`}
            </Typography>}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenNewStageDialog}
            sx={{ mr: 1 }}
          >
            Create Stage
          </Button>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<DescriptionIcon />}
            onClick={() => navigate('/templates')}
          >
            Manage Templates
          </Button>
        </Box>
        
        <Divider sx={{ mb: 3 }} />
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {stages.length === 0 ? (
              <Alert severity="info">
                No stages found. Create your first stage to get started.
              </Alert>
            ) : (
              <List sx={{ bgcolor: 'background.paper' }}>
                {[...stages].sort((a, b) => 
                  (a.stage_config?.order || Infinity) - (b.stage_config?.order || Infinity)
                ).map((stage) => (
                  <ListItem 
                    key={stage.stage_id}
                    sx={{ 
                      mb: 1,
                      bgcolor: 'background.paper'
                    }}
                  >
                    <ListItemText
                      primary={stage.stage_name}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.primary">
                            {stage.stage_description || 'No description'}
                          </Typography>
                          {stage.stage_config && stage.stage_config.order && 
                            ` • Order: ${stage.stage_config.order}`}
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Move Up">
                        <IconButton 
                          edge="end" 
                          aria-label="move-up"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMoveStage(stage.stage_id, 'up');
                          }}
                          disabled={stages.indexOf(stage) === 0}
                        >
                          <ArrowUpwardIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Move Down">
                        <IconButton 
                          edge="end" 
                          aria-label="move-down"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMoveStage(stage.stage_id, 'down');
                          }}
                          disabled={stages.indexOf(stage) === stages.length - 1}
                        >
                          <ArrowDownwardIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View Stage">
                        <IconButton 
                          edge="end" 
                          aria-label="view"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigateToStageView(stage.stage_id);
                          }}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Stage">
                        <IconButton 
                          edge="end" 
                          aria-label="delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            setStageToDelete(stage);
                            setOpenDeleteDialog(true);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </>
        )}
      </Paper>
      
      {/* Create Stage Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => !isSubmitting && setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedStage ? 'Edit Stage' : 'Create New Stage'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            {/* Add console logs to help debug */}
            {console.log("Dialog rendering with state:", {
              selectedTemplates,
              availableTemplates,
              defaultTemplates,
              templatesInfo: {
                stageSelectionCount: availableTemplates.stage_selection.length,
                dataExtractionCount: availableTemplates.data_extraction.length,
                responseGenerationCount: availableTemplates.response_generation.length,
              }
            })}
            
            {/* Stage Name */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Stage Name"
                value={newStageName}
                onChange={(e) => setNewStageName(e.target.value)}
                required
              />
            </Grid>
            
            {/* Stage Description */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Stage Description"
                value={stageDescription}
                onChange={(e) => setStageDescription(e.target.value)}
              />
            </Grid>
            
            {/* Template Selection Dropdown - Stage Selection */}
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Stage Selection Template</InputLabel>
                <Select
                  fullWidth
                  value={selectedTemplates.stage_selection}
                  onChange={(e) => handleTemplateChange(e, 'stage_selection')}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {availableTemplates.stage_selection.map((template) => (
                    <MenuItem 
                      key={template.template_id} 
                      value={template.template_id}
                      sx={template.isDefault ? { 
                        backgroundColor: 'rgba(245, 0, 87, 0.04)',
                        '&:hover': {
                          backgroundColor: 'rgba(245, 0, 87, 0.08)'
                        }
                      } : {}}
                    >
                      {template.isDefault ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <StarIcon sx={{ mr: 1, color: 'secondary.main', fontSize: '1rem' }} />
                          {template.template_name}
                        </Box>
                      ) : template.template_name}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Template for determining if this stage should handle the message</FormHelperText>
              </FormControl>
            </Grid>
            
            {/* Template Selection Dropdown - Data Extraction */}
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Data Extraction Template</InputLabel>
                <Select
                  fullWidth
                  value={selectedTemplates.data_extraction}
                  onChange={(e) => handleTemplateChange(e, 'data_extraction')}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {availableTemplates.data_extraction.map((template) => (
                    <MenuItem 
                      key={template.template_id} 
                      value={template.template_id}
                      sx={template.isDefault ? { 
                        backgroundColor: 'rgba(245, 0, 87, 0.04)',
                        '&:hover': {
                          backgroundColor: 'rgba(245, 0, 87, 0.08)'
                        }
                      } : {}}
                    >
                      {template.isDefault ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <StarIcon sx={{ mr: 1, color: 'secondary.main', fontSize: '1rem' }} />
                          {template.template_name}
                        </Box>
                      ) : template.template_name}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Template for extracting data from the message</FormHelperText>
              </FormControl>
            </Grid>
            
            {/* Template Selection Dropdown - Response Generation */}
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Response Generation Template</InputLabel>
                <Select
                  fullWidth
                  value={selectedTemplates.response_generation}
                  onChange={(e) => handleTemplateChange(e, 'response_generation')}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {availableTemplates.response_generation.map((template) => (
                    <MenuItem 
                      key={template.template_id} 
                      value={template.template_id}
                      sx={template.isDefault ? { 
                        backgroundColor: 'rgba(245, 0, 87, 0.04)',
                        '&:hover': {
                          backgroundColor: 'rgba(245, 0, 87, 0.08)'
                        }
                      } : {}}
                    >
                      {template.isDefault ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <StarIcon sx={{ mr: 1, color: 'secondary.main', fontSize: '1rem' }} />
                          {template.template_name}
                        </Box>
                      ) : template.template_name}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Template for generating responses</FormHelperText>
              </FormControl>
            </Grid>
            
            {/* Add Agent Selection Dropdown */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="agent-select-label">Agent</InputLabel>
              <Select
                labelId="agent-select-label"
                id="agent-select"
                value={selectedAgentId}
                label="Agent"
                onChange={handleAgentChange}
                disabled={isSubmitting}
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {agents.map((agent) => (
                  <MenuItem key={agent.agent_id} value={agent.agent_id}>
                    {agent.agent_name}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                Select an agent to associate with this stage
              </FormHelperText>
            </FormControl>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => !isSubmitting && setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateStage} 
            variant="contained" 
            color="primary"
            disabled={!newStageName.trim()}
            startIcon={<SaveIcon />}
          >
            Create & Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the stage "{stageToDelete?.stage_name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleDeleteStage} 
            variant="contained" 
            color="error"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert severity={snackbar.severity} onClose={handleCloseSnackbar}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default StageManager;