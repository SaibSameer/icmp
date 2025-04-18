// File: src/components/ErrorDisplay.js
import React from 'react';

function ErrorDisplay({ message }) {
    return (
        <div className="error-message">
            <strong>Error:</strong> {message}
        </div>
    );
}

export default ErrorDisplay;