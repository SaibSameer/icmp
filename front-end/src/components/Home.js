import React from 'react';
import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import BusinessList from './BusinessList';
import { useBusinessContext } from '../context/BusinessContext';

const Home = () => {
  const { selectedBusinessId } = useBusinessContext();
  const adminApiKey = sessionStorage.getItem('adminApiKey');

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to ICMP Admin
        </Typography>
        {!adminApiKey ? (
          <Typography variant="body1" paragraph>
            Please go to the <RouterLink to="/config">Configuration</RouterLink> page to enter the Admin Master API Key.
          </Typography>
        ) : (
          <Typography variant="body1" paragraph>
            Manage businesses, stages, and templates.
          </Typography>
        )}
      </Paper>

      {adminApiKey && (
        <Box>
          <BusinessList />
          
          {selectedBusinessId && (
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h5" component="h2" gutterBottom>
                    Business Details
                  </Typography>
                  <Typography variant="body1" paragraph>
                    View and manage configuration for the selected business.
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    component={RouterLink}
                    to={`/business/${selectedBusinessId}`}
                  >
                    Go to Business Details
                  </Button>
                </Paper>
              </Grid>
      
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h5" component="h2" gutterBottom>
                    Stage Management
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Create, edit, and manage stages for the selected business.
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    component={RouterLink}
                    to={`/business/${selectedBusinessId}/stages`}
                  >
                    Go to Stages
                  </Button>
                </Paper>
              </Grid>
            </Grid>
          )}
        </Box>
      )}
    </Box>
  );
};

export default Home;