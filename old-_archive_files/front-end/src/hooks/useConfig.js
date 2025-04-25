// src/hooks/useConfig.js
import { useState, useEffect, useCallback } from 'react';
import { API_CONFIG, AUTH_CONFIG } from '../config';

// Normalize UUID to ensure it passes backend validation
export const normalizeUUID = (uuid) => {
  if (!uuid) return null;
  
  try {
    // Convert to lowercase and trim whitespace
    const normalizedUUID = uuid.toLowerCase().trim();
    // Check if it's a valid UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
    
    if (uuidRegex.test(normalizedUUID)) {
      return normalizedUUID;
    }
    
    // Try to add dashes if missing but the uuid has the right length
    if (normalizedUUID.length === 32 && /^[0-9a-f]{32}$/.test(normalizedUUID)) {
      const formatted = `${normalizedUUID.slice(0, 8)}-${normalizedUUID.slice(8, 12)}-${normalizedUUID.slice(12, 16)}-${normalizedUUID.slice(16, 20)}-${normalizedUUID.slice(20)}`;
      if (uuidRegex.test(formatted)) {
        console.log(`Reformatted UUID from ${normalizedUUID} to ${formatted}`);
        return formatted;
      }
    }
    
    console.warn('Invalid UUID format:', uuid);
    return uuid; // Return original if not matching pattern
  } catch (error) {
    console.error('Error normalizing UUID:', error);
    return uuid; // Return original on error
  }
};

const useConfig = () => {
    // API keys should not be stored in localStorage. Initialize as empty.
    // They will be handled via httpOnly cookies set by the backend.
    const [apiKey, setApiKey] = useState(''); 
    const [userId, setUserId] = useState(localStorage.getItem('userId') || '');
    const [businessId, setBusinessId] = useState(localStorage.getItem('businessId') || '');
    // Business API key should also not be stored in localStorage.
    const [businessApiKey, setBusinessApiKey] = useState(''); 

    // No need to memoize simple setters like this unless performance profiling proves it necessary.
    // const memoizedSetApiKey = useCallback((newApiKey) => {
    //     setApiKey(newApiKey);
    // }, []);

    // Persist userId and businessId to localStorage when they change
    useEffect(() => {
        localStorage.setItem('userId', userId);
    }, [userId]);

    useEffect(() => {
        localStorage.setItem('businessId', businessId);
    }, [businessId]);

    return {
        apiKey,
        setApiKey, // Return the direct setter
        userId,
        setUserId,
        businessId,
        setBusinessId,
        businessApiKey,
        setBusinessApiKey, // Return the direct setter
    };
};

export default useConfig;