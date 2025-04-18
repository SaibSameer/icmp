import { useState, useEffect, useCallback } from 'react';

const useConfig = () => {
    const [apiKey, setApiKey] = useState(localStorage.getItem('icmpApiKey') || '');
    const [userId, setUserId] = useState('');
    const [businessId, setBusinessId] = useState('');
    const [validationError, setValidationError] = useState('');
    const [configOutput, setConfigOutput] = useState('');
    const [businessApiKey, setBusinessApiKey] = useState('');
    const [validationStatus, setValidationStatus] = useState(null);
    const [displayUserId, setDisplayUserId] = useState('');
    const [displayBusinessId, setDisplayBusinessId] = useState('');
    const [displayApiKey, setDisplayApiKey] = useState('');
    const [displayBusinessApiKey, setDisplayBusinessApiKey] = useState('');

    const memoizedSetApiKey = useCallback((newApiKey) => {
        setApiKey(newApiKey);
    }, []);

    return {
        apiKey,
        setApiKey: memoizedSetApiKey,
        userId,
        setUserId,
        businessId,
        setBusinessId,
        validationError,
        setValidationError,
        configOutput,
        setConfigOutput,
        businessApiKey,
        setBusinessApiKey,
        validationStatus,
        setValidationStatus,
        displayUserId,
        setDisplayUserId,
        displayBusinessId,
        setDisplayBusinessId,
        displayApiKey,
        setDisplayApiKey,
        displayBusinessApiKey,
        setDisplayBusinessApiKey
    };
};

export default useConfig;