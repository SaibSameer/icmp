import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, IconButton, CircularProgress, Alert } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { fetchUserMessages } from '../services/messageService';

const UserMessages = () => {
    const { businessId, userId } = useParams();
    const navigate = useNavigate();
    const [messages, setMessages] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const loadMessages = async () => {
            try {
                const data = await fetchUserMessages(businessId, userId);
                setMessages(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        loadMessages();
    }, [businessId, userId]);

    if (loading) return <CircularProgress />;
    if (error) return <Alert severity="error">{error}</Alert>;

    return (
        <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <IconButton 
                    onClick={() => navigate(`/business/${businessId}/messages`)}
                    sx={{ mr: 2 }}
                >
                    <ArrowBackIcon />
                </IconButton>
                <Typography variant="h4">Messages for User {userId}</Typography>
            </Box>
            
            <Box sx={{ mt: 2 }}>
                {messages.length === 0 ? (
                    <Typography>No messages found for this user.</Typography>
                ) : (
                    messages.map((message, index) => (
                        <Box 
                            key={index} 
                            sx={{ 
                                mb: 2, 
                                p: 2, 
                                bgcolor: 'background.paper',
                                borderRadius: 1,
                                boxShadow: 1
                            }}
                        >
                            <Typography variant="body1">{message.content}</Typography>
                            <Typography variant="caption" color="text.secondary">
                                {new Date(message.timestamp).toLocaleString()}
                            </Typography>
                        </Box>
                    ))
                )}
            </Box>
        </Box>
    );
};

export default UserMessages; 