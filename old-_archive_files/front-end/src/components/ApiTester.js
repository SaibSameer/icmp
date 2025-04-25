import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Divider, 
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { runAllApiTests, testApiKeyAuth, testTemplateOperations } from '../utils/apiTest';
import { getStoredCredentials } from '../utils/fetchUtils';

const ApiTester = () => {
  // Get stored credentials
  const storedCredentials = getStoredCredentials();
  
  const [businessId, setBusinessId] = useState(storedCredentials.businessId || '');
  const [businessApiKey, setBusinessApiKey] = useState(storedCredentials.businessApiKey || '');
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRunTests = async () => {
    if (!businessId || !businessApiKey) {
      setError('Business ID and API Key are required');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');
    setTestResults([]);
    
    try {
      // Test with different authentication methods
      const authMethods = [
        // Method 1: API key as query parameter
        {
          url: `/businesses/validate-credentials/?business_id=${businessId}&api_key=${businessApiKey}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        },
        // Method 2: API key in X-API-Key header
        {
          url: `/businesses/validate-credentials/?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': businessApiKey
          }
        },
        // Method 3: API key in Authorization header as Bearer token
        {
          url: `/businesses/validate-credentials/?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${businessApiKey}`
          }
        }
      ];
      
      const results = [];
      
      for (const method of authMethods) {
        try {
          console.log(`Testing with URL: ${method.url} and headers:`, method.headers);
          
          const response = await fetch(method.url, {
            method: 'GET',
            headers: method.headers,
            credentials: 'include'
          });
          
          const status = response.status;
          const data = await response.json().catch(() => ({}));
          
          const result = {
            test: 'Authentication',
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            status,
            data,
            success: response.ok
          };
          
          results.push(result);
          
          // If any method succeeds, we can stop testing
          if (response.ok) {
            setSuccess(`Authentication successful using ${result.method} method!`);
            break;
          }
        } catch (err) {
          console.error(`Error testing authentication with method:`, err);
          results.push({
            test: 'Authentication',
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            error: err.message,
            success: false
          });
        }
      }
      
      // Check if any method succeeded
      const successfulResult = results.find(r => r.success);
      
      if (!successfulResult) {
        setError('All authentication methods failed. Check the results for details.');
      }
      
      // If authentication succeeded, test templates
      if (successfulResult) {
        await handleTestTemplates();
      }
      
      setTestResults(results);
    } catch (err) {
      console.error('Test error:', err);
      setError(`Test error: ${err.message}`);
      setTestResults([{
        test: 'Authentication',
        error: err.message,
        success: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestAuth = async () => {
    if (!businessId || !businessApiKey) {
      setError('Business ID and API Key are required');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');
    setTestResults([]);
    
    try {
      // Test with different authentication methods
      const authMethods = [
        // Method 1: API key as query parameter
        {
          url: `/businesses/validate-credentials?business_id=${businessId}&api_key=${businessApiKey}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        },
        // Method 2: API key in X-API-Key header
        {
          url: `/businesses/validate-credentials?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': businessApiKey
          }
        },
        // Method 3: API key in Authorization header as Bearer token
        {
          url: `/businesses/validate-credentials?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${businessApiKey}`
          }
        }
      ];
      
      const results = [];
      
      for (const method of authMethods) {
        try {
          console.log(`Testing with URL: ${method.url} and headers:`, method.headers);
          
          const response = await fetch(method.url, {
            method: 'GET',
            headers: method.headers,
            credentials: 'include'
          });
          
          const status = response.status;
          const data = await response.json().catch(() => ({}));
          
          const result = {
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            status,
            data,
            success: response.ok
          };
          
          results.push(result);
          
          // If any method succeeds, we can stop testing
          if (response.ok) {
            setSuccess(`Authentication successful using ${result.method} method!`);
            break;
          }
        } catch (err) {
          console.error(`Error testing authentication method:`, err);
          results.push({
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            error: err.message,
            success: false
          });
        }
      }
      
      setTestResults(results);
      
      // Check if any method succeeded
      const successfulResult = results.find(r => r.success);
      
      if (!successfulResult) {
        setError('All authentication methods failed. Check the results for details.');
      }
    } catch (err) {
      console.error('Authentication test error:', err);
      setError(`Authentication test error: ${err.message}`);
      setTestResults([{
        test: 'Authentication',
        error: err.message,
        success: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestTemplates = async () => {
    if (!businessId || !businessApiKey) {
      setError('Business ID and API Key are required');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');
    setTestResults([]);
    
    try {
      // Test with different authentication methods
      const authMethods = [
        // Method 1: API key as query parameter
        {
          url: `/templates/?business_id=${businessId}&api_key=${businessApiKey}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        },
        // Method 2: API key in X-API-Key header
        {
          url: `/templates/?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': businessApiKey
          }
        },
        // Method 3: API key in Authorization header as Bearer token
        {
          url: `/templates/?business_id=${businessId}`,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${businessApiKey}`
          }
        }
      ];
      
      const results = [];
      
      for (const method of authMethods) {
        try {
          console.log(`Testing with URL: ${method.url} and headers:`, method.headers);
          
          const response = await fetch(method.url, {
            method: 'GET',
            headers: method.headers,
            credentials: 'include'
          });
          
          const status = response.status;
          const data = await response.json().catch(() => ({}));
          
          const result = {
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            status,
            data,
            success: response.ok
          };
          
          results.push(result);
          
          // If any method succeeds, we can stop testing
          if (response.ok) {
            setSuccess(`Templates fetched successfully using ${result.method} method!`);
            break;
          }
        } catch (err) {
          console.error(`Error testing templates with method:`, err);
          results.push({
            method: Object.keys(method.headers).find(h => h.includes('API') || h.includes('Authorization')) || 'query',
            error: err.message,
            success: false
          });
        }
      }
      
      setTestResults(results);
      
      // Check if any method succeeded
      const successfulResult = results.find(r => r.success);
      
      if (!successfulResult) {
        setError('All template fetch methods failed. Check the results for details.');
      }
    } catch (err) {
      console.error('Templates test error:', err);
      setError(`Templates test error: ${err.message}`);
      setTestResults([{
        test: 'Templates',
        error: err.message,
        success: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTestResults = () => {
    if (!testResults) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>Test Results</Typography>
        
        {testResults.authResult && (
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Authentication Test Results</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                {testResults.authResult.results.map((result, index) => (
                  <ListItem key={index} divider>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1">
                            {Object.keys(result.headers)[0]}
                          </Typography>
                          <Chip 
                            label={result.success ? 'Success' : 'Failed'} 
                            color={result.success ? 'success' : 'error'} 
                            size="small" 
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2">
                            Status: {result.status || 'N/A'}
                          </Typography>
                          {result.data && (
                            <Typography variant="body2">
                              Response: {JSON.stringify(result.data)}
                            </Typography>
                          )}
                          {result.error && (
                            <Typography variant="body2" color="error">
                              Error: {result.error}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        )}
        
        {testResults.templateResult && (
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Template Operations Test Results</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="subtitle1" gutterBottom>Fetch Templates</Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Status: {testResults.templateResult.fetchResult.status || 'N/A'}
                </Typography>
                <Chip 
                  label={testResults.templateResult.fetchResult.success ? 'Success' : 'Failed'} 
                  color={testResults.templateResult.fetchResult.success ? 'success' : 'error'} 
                  size="small" 
                  sx={{ mt: 1 }}
                />
                {testResults.templateResult.fetchResult.data && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Response: {JSON.stringify(testResults.templateResult.fetchResult.data)}
                  </Typography>
                )}
                {testResults.templateResult.fetchResult.error && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    Error: {testResults.templateResult.fetchResult.error}
                  </Typography>
                )}
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" gutterBottom>Create Template</Typography>
              <Box>
                <Typography variant="body2">
                  Status: {testResults.templateResult.createResult.status || 'N/A'}
                </Typography>
                <Chip 
                  label={testResults.templateResult.createResult.success ? 'Success' : 'Failed'} 
                  color={testResults.templateResult.createResult.success ? 'success' : 'error'} 
                  size="small" 
                  sx={{ mt: 1 }}
                />
                {testResults.templateResult.createResult.data && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Response: {JSON.stringify(testResults.templateResult.createResult.data)}
                  </Typography>
                )}
                {testResults.templateResult.createResult.error && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    Error: {testResults.templateResult.createResult.error}
                  </Typography>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        )}
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>API Tester</Typography>
      <Typography variant="body1" paragraph>
        Use this tool to test API connectivity and authentication. Enter your Business ID and API Key below.
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Business ID"
          value={businessId}
          onChange={(e) => setBusinessId(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          fullWidth
          label="API Key"
          value={businessApiKey}
          onChange={(e) => setBusinessApiKey(e.target.value)}
          margin="normal"
          required
          type="password"
        />
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button 
          variant="contained" 
          onClick={handleRunTests} 
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
        >
          Run All Tests
        </Button>
        <Button 
          variant="outlined" 
          onClick={handleTestAuth} 
          disabled={isLoading}
        >
          Test Authentication
        </Button>
        <Button 
          variant="outlined" 
          onClick={handleTestTemplates} 
          disabled={isLoading}
        >
          Test Templates
        </Button>
      </Box>
      
      {renderTestResults()}
    </Paper>
  );
};

export default ApiTester;