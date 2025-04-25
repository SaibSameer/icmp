import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Box, Breadcrumbs, Typography, Button } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import StageView from '../components/StageView';

function StageViewPage() {
    const { stageId } = useParams();

    return (
        <Box>
            <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
                <Breadcrumbs aria-label="breadcrumb">
                    <Link to="/stages" style={{ textDecoration: 'none', color: 'inherit' }}>
                        Stage Management
                    </Link>
                    <Typography color="text.primary">View Stage</Typography>
                </Breadcrumbs>
                <Button
                    variant="outlined"
                    startIcon={<ArrowBackIcon />}
                    component={Link}
                    to="/stages"
                >
                    Back to Stages
                </Button>
            </Box>
            <StageView />
        </Box>
    );
}

export default StageViewPage;