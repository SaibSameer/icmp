import React, { useState, useEffect } from 'react';
import {
    Typography,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    IconButton,
    CircularProgress,
    Alert,
    Button,
    Box,
    Divider,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Tooltip
} from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import StageIcon from '@mui/icons-material/Layers';
import { useNavigate } from 'react-router-dom';
import useAgents from '../hooks/useAgents';
import { createAgent, updateAgent, deleteAgent } from '../services/agentService';
import useConfig from '../hooks/useConfig';
import { normalizeUUID } from '../hooks/useConfig';

function AgentSection({ handleSnackbarOpen, onAgentSelect }) {
    console.log("Rendering AgentSection component");
    const { agents, isLoading, error, refreshAgents } = useAgents(handleSnackbarOpen);
    const [selectedAgentId, setSelectedAgentId] = useState(null);
    const { businessId } = useConfig(); // Get businessId from config
    const normalizedBusinessId = normalizeUUID(businessId);
    const navigate = useNavigate();

    // Debug logging
    useEffect(() => {
        console.log("AgentSection - Current state:", { 
            agents, 
            isLoading, 
            error, 
            businessId,
            normalizedBusinessId,
            selectedAgentId
        });
    }, [agents, isLoading, error, businessId, normalizedBusinessId, selectedAgentId]);

    // Dialog state
    const [openDialog, setOpenDialog] = useState(false);
    const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
    const [agentData, setAgentData] = useState({
        business_id: normalizedBusinessId,
        agent_name: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Update agent data whenever businessId changes
    useEffect(() => {
        setAgentData(prev => ({
            ...prev,
            business_id: normalizedBusinessId
        }));
    }, [normalizedBusinessId]);

    const handleAgentClick = (agentId) => {
        console.log("Selected Agent ID:", agentId);
        setSelectedAgentId(agentId);
        if (onAgentSelect) {
            onAgentSelect(agentId);
        }
    };

    const navigateToStageManagement = (agentId, agentName) => {
        console.log(`Navigating to stage management for agent: ${agentName} (${agentId})`);
        
        // Store agent ID in localStorage
        localStorage.setItem('agentId', agentId);
        
        // Navigate to stage management with proper URL format
        navigate(`/stage-management/business_id=${normalizedBusinessId}/agent_id=${agentId}`);
    };

    const openCreateDialog = () => {
        console.log("Opening create dialog with businessId:", normalizedBusinessId);
        setAgentData({
            business_id: normalizedBusinessId,
            agent_name: ''
        });
        setDialogMode('create');
        setOpenDialog(true);
    };

    const openEditDialog = (agent, event) => {
        if (event) event.stopPropagation();
        console.log("Opening edit dialog for agent:", agent);
        setAgentData({
            business_id: normalizedBusinessId,
            agent_name: agent.agent_name
        });
        setSelectedAgentId(agent.agent_id);
        setDialogMode('edit');
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setIsSubmitting(false);
    };

    const handleSubmit = async () => {
        if (!agentData.agent_name.trim()) {
            handleSnackbarOpen("Agent name is required", "error");
            return;
        }

        setIsSubmitting(true);
        try {
            // Make sure we're using the normalized businessId
            const submissionData = {
                ...agentData,
                business_id: normalizedBusinessId
            };
            
            console.log(`${dialogMode === 'create' ? 'Creating' : 'Updating'} agent with data:`, submissionData);
            if (dialogMode === 'create') {
                await createAgent(submissionData);
                handleSnackbarOpen("Agent created successfully", "success");
            } else {
                await updateAgent(selectedAgentId, submissionData);
                handleSnackbarOpen("Agent updated successfully", "success");
            }
            refreshAgents(); // Refresh the agents list
            handleCloseDialog();
        } catch (err) {
            console.error(dialogMode === 'create' ? "Error creating agent:" : "Error updating agent:", err);
            handleSnackbarOpen(err.message || "An error occurred", "error");
            setIsSubmitting(false);
        }
    };

    const handleDeleteAgent = async (agentId, event) => {
        if (event) event.stopPropagation();
        if (!window.confirm("Are you sure you want to delete this agent?")) return;

        try {
            if (!normalizedBusinessId) {
                throw new Error('Business ID not found');
            }

            console.log(`Deleting agent ${agentId} for business ${normalizedBusinessId}`);
            const response = await deleteAgent(agentId, normalizedBusinessId);
            if (response) {
                handleSnackbarOpen("Agent deleted successfully", "success");
                refreshAgents(); // Refresh the agents list
                if (selectedAgentId === agentId) {
                    setSelectedAgentId(null); // Clear selection if deleted agent was selected
                }
            }
        } catch (err) {
            console.error("Error deleting agent:", err);
            handleSnackbarOpen(err.message || "An error occurred while deleting the agent", "error");
        }
    };

    let agentListContent;
    if (isLoading) {
        agentListContent = (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 2 }}>
                <CircularProgress size={24} />
                <Typography sx={{ ml: 1 }} variant="body2">Loading Agents...</Typography>
            </Box>
        );
    } else if (error) {
        agentListContent = <Alert severity="error">Error loading agents: {error}</Alert>;
    } else if (agents.length > 0) {
        agentListContent = (
            <List dense>
                {agents.map((agent) => (
                    <ListItem
                        key={agent.agent_id}
                        button
                        selected={selectedAgentId === agent.agent_id}
                        onClick={() => handleAgentClick(agent.agent_id)}
                        secondaryAction={
                            <Box>
                                <Tooltip title="Manage Stages">
                                    <IconButton
                                        edge="end"
                                        aria-label="manage-stages"
                                        color="primary"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigateToStageManagement(agent.agent_id, agent.agent_name);
                                        }}
                                    >
                                        <StageIcon />
                                    </IconButton>
                                </Tooltip>
                                <IconButton
                                    edge="end"
                                    aria-label="edit"
                                    onClick={(e) => openEditDialog(agent, e)}
                                >
                                    <EditIcon />
                                </IconButton>
                                <IconButton
                                    edge="end"
                                    aria-label="delete"
                                    onClick={(e) => handleDeleteAgent(agent.agent_id, e)}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        }
                    >
                        <ListItemText
                            primary={agent.agent_name || 'Unnamed Agent'}
                            secondary={`Created: ${new Date(agent.created_at).toLocaleDateString()}`}
                        />
                    </ListItem>
                ))}
            </List>
        );
    } else {
        agentListContent = <Typography variant="body2" sx={{ p: 2, textAlign: 'center' }}>No agents found for this business.</Typography>;
    }

    return (
        <>
            <Card sx={{ mt: 2 }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6" gutterBottom component="div">
                            Agents
                        </Typography>
                        <Button
                            variant="contained"
                            size="small"
                            startIcon={<AddCircleOutlineIcon />}
                            onClick={openCreateDialog}
                        >
                            Create Agent
                        </Button>
                    </Box>
                    <Divider sx={{ mb: 1 }}/>
                    {agentListContent}
                </CardContent>
            </Card>

            {/* Create/Edit Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog}>
                <DialogTitle>{dialogMode === 'create' ? 'Create New Agent' : 'Edit Agent'}</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Agent Name"
                        fullWidth
                        variant="outlined"
                        value={agentData.agent_name}
                        onChange={(e) => setAgentData({ ...agentData, agent_name: e.target.value })}
                        disabled={isSubmitting}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} disabled={isSubmitting}>Cancel</Button>
                    <Button 
                        onClick={handleSubmit} 
                        variant="contained" 
                        disabled={isSubmitting}
                        startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
                    >
                        {dialogMode === 'create' ? 'Create' : 'Save'}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

export default AgentSection;