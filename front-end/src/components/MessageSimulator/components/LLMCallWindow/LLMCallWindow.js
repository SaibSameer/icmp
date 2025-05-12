import React, { useEffect } from 'react';
import { useLLMCalls } from '../../hooks/useLLMCalls';
import LLMCallItem from './LLMCallItem';
import './LLMCallWindow.css';

const LLMCallWindow = ({ internalApiKey }) => {
    const { calls, loading, error, refreshCalls } = useLLMCalls(internalApiKey);

    // Diagnostic: Log on mount and when state changes
    useEffect(() => {
        console.log('[LLMCallWindow] Mounted');
    }, []);
    useEffect(() => {
        console.log('[LLMCallWindow] loading:', loading);
        console.log('[LLMCallWindow] error:', error);
        console.log('[LLMCallWindow] calls:', calls);
    }, [loading, error, calls]);

    return (
        <div className="llm-call-window" style={{ border: '2px solid red', minHeight: 200 }}>
            <div className="llm-call-window-header">
                <h3>LLM Call History</h3>
                <button 
                    className="refresh-button"
                    onClick={refreshCalls}
                    title="Refresh calls"
                    disabled={loading}
                >
                    <i className={loading ? "fas fa-spinner fa-spin" : "fas fa-sync-alt"}></i>
                    {loading ? ' Refreshing...' : ' Refresh'}
                </button>
            </div>

            {/* Diagnostic debug info */}
            <div style={{ background: '#fffbe6', color: '#b36b00', padding: 8, fontSize: 12, marginBottom: 8 }}>
                <strong>Debug Info:</strong><br />
                loading: {String(loading)}<br />
                error: {error ? error.toString() : 'null'}<br />
                calls: {Array.isArray(calls) ? calls.length : 'not array'}<br />
            </div>

            {loading && (
                <div className="loading-state">
                    <i className="fas fa-spinner fa-spin"></i>
                    Loading calls...
                </div>
            )}

            {error && (
                <div className="error-state">
                    <i className="fas fa-exclamation-circle"></i>
                    {error}
                </div>
            )}

            {!loading && !error && calls.length === 0 && (
                <div className="empty-state">
                    <i className="fas fa-info-circle"></i>
                    No LLM calls found
                </div>
            )}

            <div className="llm-call-list">
                {calls.map(call => (
                    <LLMCallItem 
                        key={call.call_id} 
                        call={call}
                    />
                ))}
            </div>
        </div>
    );
};

export default LLMCallWindow; 