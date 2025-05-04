import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import { fetchConversationHistory } from '../services/messageService';
import { format, parseISO } from 'date-fns';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useNavigate } from 'react-router-dom';

const MessagePortal = ({ businessId }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const formatNullableDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(parseISO(dateString), 'PPpp');
    } catch (error) {
      console.error('Date formatting error:', error, 'Input:', dateString);
      return 'Invalid Date';
    }
  };

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchConversationHistory(businessId);
      console.log('Fetched conversation data:', data);
      
      // Group conversations by user_id and calculate total messages
      const userConversations = data.reduce((acc, conv) => {
        const userId = conv.user_id;
        if (!acc[userId]) {
          acc[userId] = {
            ...conv,
            total_messages: 0
          };
        }
        
        // Add messages from this conversation to the total
        const messageCount = conv.message_summary?.total_messages || conv.messages?.length || 0;
        acc[userId].total_messages += messageCount;
        
        // Keep the most recent conversation details
        if (conv.last_updated && (!acc[userId].last_updated || 
            parseISO(conv.last_updated) > parseISO(acc[userId].last_updated))) {
          acc[userId] = {
            ...conv,
            total_messages: acc[userId].total_messages
          };
        }
        
        return acc;
      }, {});

      // Convert back to array and sort by last_updated
      const filteredData = Object.values(userConversations).sort((a, b) => {
        const dateA = a.last_updated ? parseISO(a.last_updated) : null;
        const dateB = b.last_updated ? parseISO(b.last_updated) : null;
        if (!dateA && !dateB) return 0;
        if (!dateA) return 1;
        if (!dateB) return -1;
        return dateB - dateA;
      });
      
      setConversations(filteredData);
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch conversations. Please try again later.';
      setError(errorMessage);
      console.error('Error fetching conversations:', err);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (businessId) {
      fetchConversations();
    }
  }, [businessId]);

  const handleViewMessages = (conversationId) => {
    navigate(`/business/${businessId}/conversation/${conversationId}/messages`);
  };

  return (
    <Box sx={{ width: '100%', mt: 3 }}>
      <Typography variant="h4" gutterBottom>
        Business Conversations
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <TextField
          label="Search conversations (coming soon)"
          variant="outlined"
          size="small"
          sx={{ width: 300 }}
          disabled
        />
        <span>
          <Tooltip title="Refresh conversations">
            <span>
              <IconButton onClick={fetchConversations} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </span>
          </Tooltip>
        </span>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <Table aria-label="conversations table">
            <TableHead>
              <TableRow>
                <TableCell>User (ID)</TableCell>
                <TableCell>Start Time</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Session ID</TableCell>
                <TableCell align="right">Messages</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : conversations.length === 0 && !error ? (
                 <TableRow>
                   <TableCell colSpan={6} align="center">
                     No conversations found for this business.
                   </TableCell>
                 </TableRow>
              ) : (
                 conversations.map((conversation) => (
                   <TableRow key={conversation.conversation_id}>
                     <TableCell>
                       {conversation.user_name || 'Unknown User'} ({conversation.user_id || 'N/A'})
                     </TableCell>
                     <TableCell>{formatNullableDate(conversation.start_time)}</TableCell>
                     <TableCell>{formatNullableDate(conversation.last_updated)}</TableCell>
                     <TableCell>{conversation.session_id || 'N/A'}</TableCell>
                     <TableCell align="right">
                       {conversation.total_messages || 0}
                     </TableCell>
                     <TableCell align="center">
                       <Button
                         variant="contained"
                         color="primary"
                         size="small"
                         onClick={() => handleViewMessages(conversation.conversation_id)}
                       >
                         View Messages
                       </Button>
                     </TableCell>
                   </TableRow>
                 ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default MessagePortal;