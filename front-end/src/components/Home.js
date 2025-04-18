import React from 'react';
import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Home = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to ICMP Events API
        </Typography>
        <Typography variant="body1" paragraph>
          This application helps you manage stages and templates for your ICMP events.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" component="h2" gutterBottom>
              Business Details
            </Typography>
            <Typography variant="body1" paragraph>
              View and manage your business configuration.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              component={RouterLink}
              to="/business"
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
              Create, edit, and manage your stages for ICMP events.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              component={RouterLink}
              to="/stages"
            >
              Go to Stages
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Home;