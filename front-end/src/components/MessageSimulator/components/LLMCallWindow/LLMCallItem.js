import React from 'react';
import { formatDate, formatDuration, formatCost, truncateText } from '../../../../utils/formatters';
import './LLMCallItem.css';

const LLMCallItem = ({ call }) => {
    const {
        call_id,
        input_text,
        response,
        call_type,
        timestamp,
        duration,
        cost,
        status,
        error_message
    } = call;

    return (
        <div className="llm-call-item">
            <div className="llm-call-header">
                <span className="llm-call-type">{call_type || 'General'}</span>
                <span className="llm-call-time">{formatDate(timestamp)}</span>
            </div>
            
            <div className="llm-call-content">
                <div className="llm-call-input">
                    <h4>Input</h4>
                    <p>{truncateText(input_text, 150)}</p>
                </div>
                
                <div className="llm-call-response">
                    <h4>Response</h4>
                    <p>{truncateText(response, 150)}</p>
                </div>
            </div>
            
            <div className="llm-call-metrics">
                {duration && (
                    <span className="metric">
                        <i className="fas fa-clock"></i>
                        {formatDuration(duration)}
                    </span>
                )}
                {cost && (
                    <span className="metric">
                        <i className="fas fa-dollar-sign"></i>
                        {formatCost(cost)}
                    </span>
                )}
                {status && (
                    <span className={`status ${status.toLowerCase()}`}>
                        {status}
                    </span>
                )}
            </div>
            
            {error_message && (
                <div className="llm-call-error">
                    <i className="fas fa-exclamation-circle"></i>
                    {error_message}
                </div>
            )}
        </div>
    );
};

export default LLMCallItem; 