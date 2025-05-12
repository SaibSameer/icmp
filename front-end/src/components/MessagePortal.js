import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button
} from '@mui/material';
import { fetchUserMessageCounts } from '../services/messageService';
import { useNavigate } from 'react-router-dom';

const UserMessageCountsTable = ({ businessId }) => {
  const [data, setData] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!businessId) return;
    setLoading(true);
    fetchUserMessageCounts(businessId)
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [businessId]);

  if (loading) return <Box sx={{ my: 2 }}><CircularProgress size={20} /> Loading user message stats...</Box>;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data.length) return <Box sx={{ my: 2 }}>No user message stats found.</Box>;

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6" gutterBottom>User Message Stats</Typography>
      <TableContainer component={Paper} sx={{ maxWidth: 600 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>User ID</TableCell>
              <TableCell align="right">Messages Received</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map(row => (
              <TableRow key={row.user_id}>
                <TableCell>{row.user_id}</TableCell>
                <TableCell align="right">{row.message_count}</TableCell>
                <TableCell align="right">
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => navigate(`/business/${businessId}/messages/${row.user_id}`)}
                  >
                    View Messages
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

const MessagePortal = ({ businessId }) => {
  return (
    <Box sx={{ width: '100%', mt: 3 }}>
      <Typography variant="h4" gutterBottom>
        Business User Message Stats
      </Typography>
      <UserMessageCountsTable businessId={businessId} />
    </Box>
  );
};

export default MessagePortal;