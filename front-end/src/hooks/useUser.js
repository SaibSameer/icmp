// src/hooks/useUser.js
import { useState } from 'react';

const useUser = () => {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [userOutput, setUserOutput] = useState('');

    return {
        firstName,
        setFirstName,
        lastName,
        setLastName,
        email,
        setEmail,
        userOutput,
        setUserOutput
    };
};

export default useUser;