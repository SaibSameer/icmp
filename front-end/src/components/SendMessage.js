// File: src/components/SendMessage.js
// Last Modified: 2026-03-29

import React, { useState } from 'react';
import { TextareaAutosize, Button, Typography, Card, CardContent, Box } from '@mui/material';

function SendMessage({handleSnackbarOpen }) {
     const [messageInput, setMessageInput] = useState('');
     const [messageOutput, setMessageOutput] = useState('');

    const processMessage = async () => {
        //TODO
    };

    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Send Message</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextareaAutosize
                        minRows={3}
                        placeholder="Message"
                        style={{ width: 300, padding: 8 }}
                        value={messageInput}
                        onChange={(e) => setMessageInput(e.target.value)}
                    />
                    <Button variant="contained" onClick={processMessage}>Send</Button>
                    <Typography variant="body1">{messageOutput}</Typography>
                </Box>
            </CardContent>
        </Card>
    );
}

export default SendMessage;