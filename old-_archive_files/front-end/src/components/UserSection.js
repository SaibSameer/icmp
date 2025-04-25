import React from 'react';
import { Typography } from '@mui/material';
import UserManagement from './UserManagement';

function UserSection({ firstName, setFirstName, lastName, setLastName, email, setEmail, createUser, userOutput }) {
    return (
        <div>
            <UserManagement
                firstName={firstName}
                setFirstName={setFirstName}
                lastName={lastName}
                setLastName={setLastName}
                email={email}
                setEmail={setEmail}
                createUser={createUser}
            />
            <Typography variant="body1">{userOutput}</Typography>
        </div>
    );
}

export default UserSection;