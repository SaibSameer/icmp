import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, IconButton } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import MessagePortal from './MessagePortal';

const BusinessMessages = () => {
    const { businessId } = useParams();
    const navigate = useNavigate();

    return (
        <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <IconButton 
                    onClick={() => navigate(`/business/${businessId}`)}
                    sx={{ mr: 2 }}
                >
                    <ArrowBackIcon />
                </IconButton>
                <Typography variant="h4">Business Messages</Typography>
            </Box>
            
            <MessagePortal businessId={businessId} />
        </Box>
    );
};

export default BusinessMessages;