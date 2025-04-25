import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert
} from '@mui/material';

const TemplateSection = ({
  templateId,
  templateName,
  templateContent,
  templateSystemPrompt,
  templateType,
  setTemplateId,
  setTemplateName,
  setTemplateContent,
  setTemplateSystemPrompt,
  setTemplateType,
  createTemplate,
  errorMessage
}) => {
  const [isCreating, setIsCreating] = useState(false);

  const templateTypes = [
    { value: 'stage_selection', label: 'Stage Selection' },
    { value: 'data_extraction', label: 'Data Extraction' },
    { value: 'response_generation', label: 'Response Generation' },
    { value: 'default_stage_selection', label: 'Default Stage Selection' },
    { value: 'default_data_extraction', label: 'Default Data Extraction' },
    { value: 'default_response_generation', label: 'Default Response Generation' }
  ];

  const handleCreateTemplate = async () => {
    setIsCreating(true);
    try {
      await createTemplate();
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Create Template
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Template ID"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              margin="normal"
              disabled
              helperText="Template ID will be auto-generated"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Template Name"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              margin="normal"
              placeholder="Enter a descriptive name"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="template-type-label">Template Type</InputLabel>
              <Select
                labelId="template-type-label"
                value={templateType}
                onChange={(e) => setTemplateType(e.target.value)}
                label="Template Type"
              >
                {templateTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Template Content"
              value={templateContent}
              onChange={(e) => setTemplateContent(e.target.value)}
              margin="normal"
              multiline
              rows={6}
              placeholder="Enter template content with variables in curly braces, e.g. {variable_name}"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="System Prompt (Optional)"
              value={templateSystemPrompt}
              onChange={(e) => setTemplateSystemPrompt(e.target.value)}
              margin="normal"
              multiline
              rows={3}
              placeholder="Enter optional system prompt for the model"
            />
          </Grid>

          {errorMessage && (
            <Grid item xs={12}>
              <Alert severity="error" sx={{ mt: 2 }}>
                {errorMessage}
              </Alert>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleCreateTemplate}
                disabled={
                  isCreating || 
                  !templateName.trim() || 
                  !templateContent.trim() || 
                  !templateType
                }
              >
                {isCreating ? 'Creating...' : 'Create Template'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default TemplateSection;