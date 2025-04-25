import React, { useState, useEffect } from 'react';
import { getHealthCheck } from '../services/healthCheckService';
import ErrorDisplay from './ErrorDisplay';
import LoadingIndicator from './LoadingIndicator';
import './HealthCheck.css'; // Import the CSS file

function HealthCheck() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getHealthCheck();
        setHealthData(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();
  }, []);

  if (loading) {
    return <LoadingIndicator />;
  }

  if (error) {
    return <ErrorDisplay message={error} />;
  }

  return (
    <div className="health-check-container">
      <h2>Health Check</h2>
      {healthData && (
        <div className="health-data">
          <p><strong>Status:</strong> {healthData.status}</p>
          <p><strong>Date:</strong> {healthData.date}</p>
          <p><strong>Database:</strong> {healthData.database}</p>
          <p><strong>Schemas Loaded:</strong> {healthData.schemas_loaded}</p>
        </div>
      )}
    </div>
  );
}

export default HealthCheck;