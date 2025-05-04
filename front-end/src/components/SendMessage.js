// File: src/components/SendMessage.js
// Last Modified: 2026-03-29

import React, { useState, useEffect } from 'react';
import { TextareaAutosize, Button, Typography, Card, CardContent, Box } from '@mui/material';
import { sendMessage } from '../services/messageService';
import { getStoredCredentials } from '../services/authService';

function SendMessage({ handleSnackbarOpen, onMessageSent }) {
    const [messageInput, setMessageInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);

    const processMessage = async () => {
        if (!messageInput.trim()) {
            handleSnackbarOpen('error', 'Please enter a message');
            return;
        }

        setIsLoading(true);
        try {
            const { userId, businessId } = getStoredCredentials();
            const response = await sendMessage(messageInput, businessId, userId, {
                conversationId: conversationId
            });
            
            if (response.success) {
                // Store the conversation ID for future messages
                if (response.conversation_id) {
                    setConversationId(response.conversation_id);
                }
                
                handleSnackbarOpen('success', 'Message sent successfully');
                setMessageInput('');
                if (onMessageSent) {
                    onMessageSent(); // Trigger refresh of messages
                }
            } else {
                handleSnackbarOpen('error', response.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            handleSnackbarOpen('error', 'Failed to send message');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Send Message</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextareaAutosize
                        minRows={3}
                        placeholder="Type your message here..."
                        style={{ width: '100%', padding: 8 }}
                        value={messageInput}
                        onChange={(e) => setMessageInput(e.target.value)}
                        disabled={isLoading}
                    />
                    <Button 
                        variant="contained" 
                        onClick={processMessage}
                        disabled={isLoading || !messageInput.trim()}
                    >
                        {isLoading ? 'Sending...' : 'Send'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
}

export default SendMessage;