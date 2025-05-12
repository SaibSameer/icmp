import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Container,
  CircularProgress,
  Alert,
  Divider,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
  Tabs,
  Tab
} from '@mui/material';
import { useParams } from 'react-router-dom';
import templateService from '../../services/templateService';

function TemplateTestPage() {
  const { businessId } = useParams();
  const [templates, setTemplates] = useState([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [contextOverride, setContextOverride] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  // Template type specific test data
  const [testData, setTestData] = useState({
    message_content: '',
    field_name: '',
    fields_to_extract: [],
    available_stages: [],
    extracted_data: {}
  });

  useEffect(() => {
    if (businessId) {
      fetchTemplates();
    }
  }, [businessId]);

  const fetchTemplates = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await templateService.getTemplates(businessId);
      setTemplates(response);
      if (response.length > 0) {
        setSelectedTemplateId(response[0].template_id);
        setSelectedTemplate(response[0]);
      }
    } catch (err) {
      setError('Failed to fetch templates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTemplateId && templates.length > 0) {
      const tmpl = templates.find(t => t.template_id === selectedTemplateId);
      setSelectedTemplate(tmpl);
      setTestResult(null);
      setContextOverride('');
      // Reset test data when template changes
      setTestData({
        message_content: '',
        field_name: '',
        fields_to_extract: [],
        available_stages: [],
        extracted_data: {}
      });
    }
  }, [selectedTemplateId, templates]);

  const handleTest = async () => {
    if (!selectedTemplate) return;
    setTestLoading(true);
    setError('');
    setTestResult(null);
    try {
      // Prepare test data based on template type
      let testContext = {};
      switch (selectedTemplate.template_type) {
        case 'extraction':
          testContext = {
            message_content: testData.message_content || "Test message for extraction",
            field_name: testData.field_name || "test_field",
            fields_to_extract: testData.fields_to_extract.length > 0 ? testData.fields_to_extract : ["name", "email"],
            conversation_history: [
              { sender: 'user', content: testData.message_content || "Test message for extraction" }
            ]
          };
          break;
        case 'selection':
          testContext = {
            message_content: testData.message_content || "Test message for stage selection",
            available_stages: testData.available_stages.length > 0 ? testData.available_stages : ["stage1", "stage2", "stage3"],
            conversation_history: [
              { sender: 'user', content: testData.message_content || "Test message for stage selection" }
            ]
          };
          break;
        case 'generation':
          testContext = {
            message_content: testData.message_content || "Test message for response generation",
            extracted_data: Object.keys(testData.extracted_data).length > 0 ? testData.extracted_data : {
              name: "Test User",
              email: "test@example.com"
            },
            conversation_history: [
              { sender: 'user', content: testData.message_content || "Test message for response generation" }
            ]
          };
          break;
      }

      // Allow context override for advanced users
      if (contextOverride) {
        try {
          const overrideObj = JSON.parse(contextOverride);
          testContext = { ...testContext, ...overrideObj };
        } catch (e) {
          setError('Context override must be valid JSON.');
          setTestLoading(false);
          return;
        }
      }

      const result = await templateService.testTemplate(
        businessId,
        null,
        {
          ...selectedTemplate,
          test_context: testContext
        }
      );
      setTestResult(result.content || result.results || result);
    } catch (err) {
      setError('Failed to test template: ' + (err.message || 'Unknown error'));
    } finally {
      setTestLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const renderTestInputs = () => {
    if (!selectedTemplate) return null;

    switch (selectedTemplate.template_type) {
      case 'extraction':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message Content"
                value={testData.message_content}
                onChange={(e) => setTestData({ ...testData, message_content: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Field Name"
                value={testData.field_name}
                onChange={(e) => setTestData({ ...testData, field_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Fields to Extract (comma-separated)"
                value={testData.fields_to_extract.join(', ')}
                onChange={(e) => setTestData({ 
                  ...testData, 
                  fields_to_extract: e.target.value.split(',').map(f => f.trim()) 
                })}
              />
            </Grid>
          </Grid>
        );
      case 'selection':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message Content"
                value={testData.message_content}
                onChange={(e) => setTestData({ ...testData, message_content: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Available Stages (comma-separated)"
                value={testData.available_stages.join(', ')}
                onChange={(e) => setTestData({ 
                  ...testData, 
                  available_stages: e.target.value.split(',').map(s => s.trim()) 
                })}
              />
            </Grid>
          </Grid>
        );
      case 'generation':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message Content"
                value={testData.message_content}
                onChange={(e) => setTestData({ ...testData, message_content: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Extracted Data (JSON)"
                value={JSON.stringify(testData.extracted_data, null, 2)}
                onChange={(e) => {
                  try {
                    const data = JSON.parse(e.target.value);
                    setTestData({ ...testData, extracted_data: data });
                  } catch (err) {
                    // Invalid JSON, don't update
                  }
                }}
                multiline
                rows={4}
                error={!isValidJson(testData.extracted_data)}
                helperText={!isValidJson(testData.extracted_data) ? "Invalid JSON format" : ""}
              />
            </Grid>
          </Grid>
        );
      default:
        return null;
    }
  };

  const isValidJson = (obj) => {
    try {
      JSON.stringify(obj);
      return true;
    } catch (e) {
      return false;
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Template Test Page
        </Typography>
        <Divider sx={{ mb: 3 }} />
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Template</InputLabel>
              <Select
                value={selectedTemplateId}
                label="Select Template"
                onChange={e => setSelectedTemplateId(e.target.value)}
              >
                {templates.map(tmpl => (
                  <MenuItem key={tmpl.template_id} value={tmpl.template_id}>
                    {tmpl.template_name} ({tmpl.template_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {selectedTemplate && (
              <>
                <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
                  <Tab label="Template" />
                  <Tab label="Test Data" />
                  <Tab label="Advanced" />
                </Tabs>

                {activeTab === 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">Template Content:</Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f5f5f5', mb: 2 }}>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{selectedTemplate.content}</pre>
                    </Paper>
                    <Typography variant="subtitle2">System Prompt:</Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f5f5f5', mb: 2 }}>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{selectedTemplate.system_prompt}</pre>
                    </Paper>
                  </Box>
                )}

                {activeTab === 1 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Test Data for {selectedTemplate.template_type} Template:
                    </Typography>
                    {renderTestInputs()}
                  </Box>
                )}

                {activeTab === 2 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Context Override (JSON):
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      value={contextOverride}
                      onChange={(e) => setContextOverride(e.target.value)}
                      placeholder="Enter JSON to override context variables"
                      error={contextOverride && !isValidJson(contextOverride)}
                      helperText={contextOverride && !isValidJson(contextOverride) ? "Invalid JSON format" : ""}
                    />
                  </Box>
                )}

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleTest}
                    disabled={testLoading}
                  >
                    {testLoading ? <CircularProgress size={24} /> : 'Test Template'}
                  </Button>
                </Box>

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}

                {testResult && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Test Result
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {typeof testResult === 'string' ? testResult : JSON.stringify(testResult, null, 2)}
                      </pre>
                    </Paper>
                  </Box>
                )}
              </>
            )}
          </>
        )}
      </Paper>
    </Container>
  );
}

export default TemplateTestPage; 