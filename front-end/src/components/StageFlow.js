import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

const StageFlow = ({ stages, businessId, agentId }) => {
  const [transitions, setTransitions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTransition, setSelectedTransition] = useState(null);
  const [newTransition, setNewTransition] = useState({
    from_stage_id: '',
    to_stage_id: '',
    condition: '',
    priority: 1
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchTransitions = useCallback(async () => {
    if (!businessId) {
      setError('Business ID is required');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      // Include agent_id in the query params if it exists
      const queryParams = new URLSearchParams({
        business_id: businessId
      });
      
      if (agentId) {
        queryParams.append('agent_id', agentId);
      }

      const response = await fetch(`/transitions?${queryParams.toString()}`, {
        credentials: 'include',
      });
      
      if (!response.ok) throw new Error('Failed to fetch transitions');
      const data = await response.json();
      setTransitions(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch transitions');
    } finally {
      setIsLoading(false);
    }
  }, [businessId, agentId]);

  useEffect(() => {
    fetchTransitions();
  }, [fetchTransitions]);

  const handleCreateTransition = async () => {
    if (!newTransition.from_stage_id || !newTransition.to_stage_id) {
      setError('From stage and To stage are required');
      return;
    }

    setIsLoading(true);
    try {
      // Include agent_id in the transition data if it exists
      const transitionData = {
        ...newTransition,
        business_id: businessId,
        ...(agentId && { agent_id: agentId })
      };

      const response = await fetch('/transitions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(transitionData),
      });
      
      if (!response.ok) throw new Error('Failed to create transition');
      const data = await response.json();
      setTransitions([...transitions, data]);
      setOpenDialog(false);
      setNewTransition({
        from_stage_id: '',
        to_stage_id: '',
        condition: '',
        priority: 1
      });
      setSuccess('Transition created successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTransition = async (transitionId) => {
    if (!window.confirm('Are you sure you want to delete this transition?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/transitions/${transitionId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      
      if (!response.ok) throw new Error('Failed to delete transition');
      setTransitions(transitions.filter(t => t.transition_id !== transitionId));
      setSuccess('Transition deleted successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getStageNameById = (stageId) => {
    const stage = stages.find(s => s.stage_id === stageId);
    return stage ? stage.stage_name : 'Unknown Stage';
  };

  // Filter stages by agent_id if needed
  const filteredStages = agentId 
    ? stages.filter(stage => !stage.agent_id || stage.agent_id === agentId)
    : stages;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Stage Transitions {agentId ? 'for Selected Agent' : ''}
        </Typography>
        <Button
          variant="contained"
          onClick={() => {
            setSelectedTransition(null);
            setNewTransition({
              from_stage_id: '',
              to_stage_id: '',
              condition: '',
              priority: 1
            });
            setOpenDialog(true);
          }}
          disabled={filteredStages.length < 2}
        >
          Add Transition
        </Button>
      </Box>

      {filteredStages.length < 2 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You need at least two stages to create transitions.
        </Alert>
      )}

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      )}

      {!isLoading && !error && transitions.length === 0 && (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography>No transitions defined yet.</Typography>
        </Paper>
      )}

      {!isLoading && !error && transitions.length > 0 && (
        <Grid container spacing={2}>
          {transitions.map((transition) => (
            <Grid item xs={12} md={6} key={transition.transition_id}>
              <Paper sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle1">
                    {getStageNameById(transition.from_stage_id)} → {getStageNameById(transition.to_stage_id)}
                  </Typography>
                  <Button 
                    variant="outlined" 
                    color="error" 
                    size="small"
                    onClick={() => handleDeleteTransition(transition.transition_id)}
                  >
                    Delete
                  </Button>
                </Box>
                <Typography variant="body2">
                  <strong>Condition:</strong> {transition.condition || 'Unconditional'}
                </Typography>
                <Typography variant="body2">
                  <strong>Priority:</strong> {transition.priority}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedTransition ? 'Edit Transition' : 'Create New Transition'}
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>From Stage</InputLabel>
            <Select
              value={newTransition.from_stage_id}
              onChange={(e) => setNewTransition({ ...newTransition, from_stage_id: e.target.value })}
              label="From Stage"
            >
              {filteredStages.map((stage) => (
                <MenuItem key={stage.stage_id} value={stage.stage_id}>
                  {stage.stage_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>To Stage</InputLabel>
            <Select
              value={newTransition.to_stage_id}
              onChange={(e) => setNewTransition({ ...newTransition, to_stage_id: e.target.value })}
              label="To Stage"
            >
              {filteredStages.map((stage) => (
                <MenuItem key={stage.stage_id} value={stage.stage_id}>
                  {stage.stage_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Condition"
            value={newTransition.condition}
            onChange={(e) => setNewTransition({ ...newTransition, condition: e.target.value })}
            sx={{ mt: 2 }}
            helperText="Enter the condition that triggers this transition (e.g., 'user_agreed', 'payment_completed')"
          />

          <TextField
            margin="dense"
            label="Priority"
            type="number"
            fullWidth
            value={newTransition.priority}
            onChange={(e) => setNewTransition({ ...newTransition, priority: parseInt(e.target.value) || 1 })}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTransition} variant="contained">
            {selectedTransition ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default StageFlow;