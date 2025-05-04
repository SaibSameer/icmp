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
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Button,
  TextField,
  Grid,
  Tooltip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchConversationHistory, sendMessage, stopAIResponses } from '../services/messageService';
import { format, parseISO } from 'date-fns';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SendIcon from '@mui/icons-material/Send';
import StopIcon from '@mui/icons-material/Stop';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const ConversationMessages = () => {
  const { businessId, conversationId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [conversationDetails, setConversationDetails] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [aiStopped, setAiStopped] = useState(false);
  const [stopping, setStopping] = useState(false);

  const formatNullableDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(parseISO(dateString), 'PPpp');
    } catch (error) {
      console.error('Date formatting error:', error, 'Input:', dateString);
      return 'Invalid Date';
    }
  };

  const fetchMessages = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchConversationHistory(businessId);
      console.log('All conversations data:', data);
      
      // Find the current conversation to get user details
      const currentConversation = data.find(conv => conv.conversation_id === conversationId);
      console.log('Current conversation:', currentConversation);
      
      if (currentConversation) {
        setConversationDetails(currentConversation);
        
        // Get all conversations for this user
        const userConversations = data.filter(conv => conv.user_id === currentConversation.user_id);
        console.log('All user conversations:', userConversations);
        
        // Collect all messages from all conversations for this user
        let allMessages = [];
        userConversations.forEach(conv => {
          if (Array.isArray(conv.messages)) {
            // Ensure each message has the conversation_id
            const messagesWithConvId = conv.messages.map(msg => ({
              ...msg,
              conversation_id: conv.conversation_id
            }));
            allMessages = [...allMessages, ...messagesWithConvId];
          }
        });
        
        // Map messages to ensure consistent structure
        const processedMessages = allMessages.map(msg => {
          // Determine message type based on sender_type
          const senderType = msg.sender_type || (msg.is_from_agent ? 'assistant' : 'user');
          
          return {
            message_id: msg.message_id || msg.id,
            content: msg.content || msg.message_content,
            message_content: msg.message_content || msg.content,
            sender_type: senderType,
            timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
            is_from_agent: senderType !== 'user',
            stage_id: msg.stage_id,
            conversation_id: msg.conversation_id
          };
        });
        
        // Sort messages by timestamp
        processedMessages.sort((a, b) => {
          const dateA = new Date(a.timestamp);
          const dateB = new Date(b.timestamp);
          return dateA - dateB;
        });
        
        console.log('Processed messages:', processedMessages);
        setMessages(processedMessages);
      } else {
        setError('Conversation not found');
        setMessages([]);
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch messages. Please try again later.';
      setError(errorMessage);
      console.error('Error fetching messages:', err);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIStatus = async () => {
    try {
      const response = await stopAIResponses(conversationId, null, 'status');
      setAiStopped(response.status?.is_stopped || false);
    } catch (err) {
      console.error('Error fetching AI status:', err);
    }
  };

  useEffect(() => {
    if (businessId && conversationId) {
      fetchMessages();
      fetchAIStatus();
    }
  }, [businessId, conversationId]);

  // Add debug effect for messages state
  useEffect(() => {
    console.log('Current messages state:', messages);
  }, [messages]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      setSending(true);
      setError(null);
      
      // Get user ID from conversation details
      const userId = conversationDetails?.user_id;
      if (!userId) {
        throw new Error('User ID not found in conversation details');
      }

      // Create a temporary message object for immediate display
      const tempMessageObj = {
        message_id: 'temp-' + Date.now(),
        content: newMessage,
        message_content: newMessage,
        sender_type: 'staff',
        timestamp: new Date().toISOString(),
        is_from_agent: true,
        conversation_id: conversationId
      };
      
      // Add the temporary message to the UI immediately
      setMessages(prevMessages => [...prevMessages, tempMessageObj]);
      
      // Clear input early to improve UX
      setNewMessage('');

      const response = await sendMessage(newMessage, businessId, userId, {
        conversationId: conversationId,
        senderType: 'staff'
      });
      
      console.log('Message sent successfully:', response);
      
      // Replace temporary message with actual message from response
      const actualMessageObj = {
        message_id: response.message_id,
        content: newMessage,
        message_content: newMessage,
        sender_type: 'staff',
        timestamp: new Date().toISOString(),
        is_from_agent: true,
        conversation_id: response.conversation_id || conversationId
      };
      
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.message_id === tempMessageObj.message_id ? actualMessageObj : msg
        )
      );
      
      // If we have a new conversation ID, update it
      if (response.conversation_id && response.conversation_id !== conversationId) {
        console.log('Updating conversation ID from', conversationId, 'to', response.conversation_id);
        navigate(`/business/${businessId}/conversation/${response.conversation_id}/messages`, { replace: true });
      }
      
      // Add AI response if it exists
      if (response.response) {
        const aiMessageObj = {
          message_id: response.process_log_id,
          content: response.response,
          message_content: response.response,
          sender_type: 'assistant',
          timestamp: new Date().toISOString(),
          is_from_agent: true,
          conversation_id: response.conversation_id || conversationId
        };
        setMessages(prevMessages => [...prevMessages, aiMessageObj]);
      }
      
      // Fetch latest messages to ensure we're in sync, but preserve current messages
      const currentMessages = messages;
      await fetchMessages();
      if (messages.length < currentMessages.length) {
        setMessages(currentMessages);
      }

    } catch (err) {
      const errorMessage = err.message || 'Failed to send message. Please try again later.';
      setError(errorMessage);
      console.error('Error sending message:', err);
      
      // Remove the temporary message on error
      setMessages(prevMessages => 
        prevMessages.filter(msg => msg.message_id !== 'temp-' + Date.now())
      );
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleStopAI = async () => {
    try {
      setStopping(true);
      setError(null);
      const response = await stopAIResponses(conversationId, null, aiStopped ? 'resume' : 'stop');
      if (response.success) {
        setAiStopped(response.status.is_stopped);
        console.log('AI control response:', response);
      } else {
        setError(response.error || 'Failed to control AI responses');
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to control AI responses. Please try again later.';
      setError(errorMessage);
      console.error('Error controlling AI:', err);
    } finally {
      setStopping(false);
    }
  };

  return (
    <Box sx={{ 
      width: '100%', 
      p: 3, 
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh',
      position: 'relative'
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton 
          onClick={() => navigate(`/business/${businessId}/messages`)}
          sx={{ mr: 2 }}
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4">
          Conversation Messages
        </Typography>
        <Box sx={{ ml: 'auto' }}>
          <Tooltip title={aiStopped ? "Resume AI Responses" : "Stop AI Responses"}>
            <Button
              variant="contained"
              color={aiStopped ? "success" : "error"}
              startIcon={aiStopped ? <PlayArrowIcon /> : <StopIcon />}
              onClick={handleStopAI}
              disabled={stopping}
              sx={{ ml: 2 }}
            >
              {stopping ? 'Processing...' : (aiStopped ? 'Resume AI' : 'Stop AI')}
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {conversationDetails && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">
            User: {conversationDetails.user_name || 'Unknown User'}
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Started: {formatNullableDate(conversationDetails.start_time)}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Conversation ID: {conversationId}
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        flexDirection: 'column',
        minHeight: 0 // This is important for the flex layout
      }}>
        <Paper sx={{ 
          width: '100%', 
          mb: 2, 
          flexGrow: 1, 
          overflow: 'auto',
          position: 'relative'
        }}>
          <TableContainer>
            <Table aria-label="messages table">
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Sender</TableCell>
                  <TableCell>Content</TableCell>
                  <TableCell>Stage ID</TableCell>
                  <TableCell>Message ID</TableCell>
                  <TableCell>Conversation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : messages.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No messages found in this conversation.
                    </TableCell>
                  </TableRow>
                ) : (
                  messages.map((message) => {
                    console.log('Rendering message:', message);
                    return (
                      <TableRow 
                        key={message.message_id}
                        sx={{
                          backgroundColor: message.conversation_id === conversationId ? 'rgba(0, 0, 0, 0.04)' : 'inherit'
                        }}
                      >
                        <TableCell>{formatNullableDate(message.timestamp)}</TableCell>
                        <TableCell>
                          {message.sender_type === 'user' ? 'User' :
                           message.sender_type === 'staff' ? 'Staff' :
                           message.sender_type === 'assistant' || message.sender_type === 'ai' ? 'Assistant' : 
                           message.is_from_agent ? 'Assistant' : 'User'}
                        </TableCell>
                        <TableCell>{message.message_content || message.content || 'N/A'}</TableCell>
                        <TableCell>{message.stage_id || conversationDetails.stage_id || 'N/A'}</TableCell>
                        <TableCell>{message.message_id}</TableCell>
                        <TableCell>
                          {message.conversation_id === conversationId ? 
                            'Current Conversation' : 
                            `Conversation ${message.conversation_id?.slice(0, 8)}...`
                          }
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        <Paper sx={{ 
          p: 2, 
          position: 'sticky',
          bottom: 0,
          backgroundColor: 'white',
          zIndex: 1,
          boxShadow: '0px -2px 4px rgba(0,0,0,0.1)'
        }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                variant="outlined"
                placeholder="Type your message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={sending}
                sx={{ backgroundColor: 'white' }}
              />
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                onClick={handleSendMessage}
                disabled={sending || !newMessage.trim()}
              >
                {sending ? 'Sending...' : 'Send'}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Box>
  );
};

export default ConversationMessages;