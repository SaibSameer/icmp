import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Tabs,
  Tab
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import StageManager from './StageManager';

const Business = ({ 
  handleLogout, 
  userId, 
  businessId, 
  businessApiKey 
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleLogoutClick = () => {
    handleLogout();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Business Dashboard</Typography>
        <Button
          startIcon={<LogoutIcon />}
          onClick={handleLogoutClick}
          variant="outlined"
          color="error"
        >
          Logout
        </Button>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Configuration" />
          <Tab label="Stages" />
          <Tab label="Analytics" />
        </Tabs>
      </Paper>

      {activeTab === 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Current Configuration
          </Typography>
          <Divider sx={{ my: 1 }} />
          <List>
            <ListItem>
              <ListItemText
                primary="User ID"
                secondary={userId || 'Not set'}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Business ID"
                secondary={businessId || 'Not set'}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Business API Key"
                secondary={businessApiKey ? `${businessApiKey.slice(0, 8)}...` : 'Not set'}
              />
            </ListItem>
          </List>
        </Paper>
      )}

      {activeTab === 1 && (
        <StageManager businessId={businessId} />
      )}

      {activeTab === 2 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Analytics Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Analytics features coming soon...
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default Business;