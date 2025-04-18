import React from 'react';
import useBusiness from '../../hooks/useBusiness';
import { Box, Typography, Paper } from '@mui/material';

const BusinessSection = ({ handleSnackbarOpen }) => {
  const { businessDetails, isLoading, error } = useBusiness(handleSnackbarOpen);

  if (isLoading) {
    return (
      <Paper elevation={1} sx={{ p: 2, my: 2 }}>
        <Typography>Loading Business Details...</Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={1} sx={{ p: 2, my: 2 }}>
        <Typography color="error">Error loading business details</Typography>
      </Paper>
    );
  }

  if (!businessDetails) {
    return (
      <Paper elevation={1} sx={{ p: 2, my: 2 }}>
        <Typography>Business details will load here</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={1} sx={{ p: 2, my: 2 }}>
      <Box>
        <Typography variant="h6" gutterBottom>
          {businessDetails.name}
        </Typography>
        <Typography>{businessDetails.address}</Typography>
        <Typography>{businessDetails.phone}</Typography>
        <Typography>{businessDetails.email}</Typography>
      </Box>
    </Paper>
  );
};

export default BusinessSection;