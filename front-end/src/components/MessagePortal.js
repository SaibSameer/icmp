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
  Collapse,
  TableSortLabel
} from '@mui/material';
import { fetchConversationHistory } from '../services/messageService';
import { format, parseISO } from 'date-fns';
import RefreshIcon from '@mui/icons-material/Refresh';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

const ConversationRow = ({ conversation, onFetchError }) => {
  const [open, setOpen] = useState(false);

  const formatNullableDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(parseISO(dateString), 'PPpp');
    } catch (error) {
      console.error('Date formatting error:', error, 'Input:', dateString);
      onFetchError(`Error formatting date: ${dateString}`);
      return 'Invalid Date';
    }
  };

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          {conversation.user_name || 'Unknown User'} ({conversation.user_id || 'N/A'})
        </TableCell>
        <TableCell>{formatNullableDate(conversation.last_updated)}</TableCell>
        <TableCell>{conversation.session_id || 'N/A'}</TableCell>
        <TableCell>{conversation.stage_id || 'N/A'}</TableCell>
        <TableCell align="right">{conversation.messages?.length ?? 0}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Messages
              </Typography>
              <Table size="small" aria-label="messages">
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Sender</TableCell>
                    <TableCell>Content</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {conversation.messages && conversation.messages.length > 0 ? (
                    conversation.messages.map((message) => (
                      <TableRow key={message.message_id}>
                        <TableCell component="th" scope="row">
                          {formatNullableDate(message.timestamp)}
                        </TableCell>
                        <TableCell>{message.sender ?? 'N/A'}</TableCell>
                        <TableCell>{message.content ?? 'N/A'}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                     <TableRow>
                       <TableCell colSpan={3} align="center">No messages in this conversation.</TableCell>
                     </TableRow>
                  )}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
};

const MessagePortal = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchConversationHistory();
      data.sort((a, b) => {
          const dateA = a.last_updated ? parseISO(a.last_updated) : null;
          const dateB = b.last_updated ? parseISO(b.last_updated) : null;
          if (!dateA && !dateB) return 0;
          if (!dateA) return 1;
          if (!dateB) return -1;
          return dateB - dateA;
      });
      setConversations(data);
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch conversations. Please try again later.';
      setError(errorMessage);
      console.error('Error fetching conversations:', err);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChildError = (errorMessage) => {
    if (!error) {
      setError(errorMessage);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

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
            <IconButton onClick={fetchConversations} disabled={loading}>
              <RefreshIcon />
            </IconButton>
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
          <Table aria-label="collapsible table">
            <TableHead>
              <TableRow>
                <TableCell />
                <TableCell>User (ID)</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Session ID</TableCell>
                <TableCell>Stage ID</TableCell>
                <TableCell align="right">Messages</TableCell>
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
                  <ConversationRow key={conversation.conversation_id} conversation={conversation} onFetchError={handleChildError} />
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