// src/components/UserManagement.js
import React from 'react';
import { TextField, Button, Typography, Card, CardContent, Box } from '@mui/material';

function UserManagement({ firstName, setFirstName, lastName, setLastName, email, setEmail, userOutput, createUser, handleSnackbarOpen }) {
    return (
        <Card sx={{ mt: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>User Management</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <TextField label="First Name" variant="outlined" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                    <TextField label="Last Name" variant="outlined" value={lastName} onChange={(e) => setLastName(e.target.value)} />
                    <TextField label="Email" variant="outlined" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <Button variant="contained" onClick={createUser}>Create User</Button>
                    <Typography variant="body1">{userOutput}</Typography>
                </Box>
            </CardContent>
        </Card>
    );
}

export default UserManagement;