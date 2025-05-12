import { useState, useEffect, useCallback, useRef } from 'react';
import llmService from '../../../services/llmService';

export const useLLMCalls = (internalApiKey, limit = 10) => {
    const [calls, setCalls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const mounted = useRef(true);

    const fetchCalls = useCallback(async () => {
        if (!mounted.current) return;
        
        try {
            setLoading(true);
            setError(null);
            if (!internalApiKey) {
                setError('Internal API key required');
                setCalls([]);
                return;
            }
            const data = await llmService.getRecentCalls(internalApiKey, limit);
            if (mounted.current) {
                setCalls(data);
            }
        } catch (err) {
            if (mounted.current) {
                setError(err.message);
                console.error('Error fetching LLM calls:', err);
            }
        } finally {
            if (mounted.current) {
                setLoading(false);
            }
        }
    }, [internalApiKey, limit]);

    useEffect(() => {
        mounted.current = true;
        fetchCalls();
        
        return () => {
            mounted.current = false;
        };
    }, [fetchCalls]);

    return {
        calls,
        loading,
        error,
        refreshCalls: fetchCalls
    };
}; 