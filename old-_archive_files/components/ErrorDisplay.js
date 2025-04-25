import React from 'react';

function ErrorDisplay({ message }) {
  return (
    <div style={{ color: 'red', margin: '10px' }}>
      <strong>Error:</strong> {message}
    </div>
  );
}

export default ErrorDisplay;