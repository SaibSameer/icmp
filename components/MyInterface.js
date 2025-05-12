// File: src/components/MyInterface.js
// Last Modified: 2026-03-30
import React, { useState, useEffect } from 'react';
import './MyInterface.css';
import {
    TextField, Button, Typography, Card, CardContent, Box, TextareaAutosize,
    Snackbar, Alert, Grid, Select, MenuItem, InputLabel, FormControl
} from '@mui/material';
import {
    saveConfig as saveConfigApi,
    createUser as createUserApi,
    fetchBusinessDetails as fetchBusinessDetailsApi,
    createTemplate as createTemplateApi,
    fetchTemplates as fetchTemplatesApi,
    createStage as createStageApi,
    fetchStages as fetchStagesApi,
    processMessage as processMessageApi,
    getStage as getStageApi, // new one
    updateStage as updateStageApi, // new one
    getDefaultTemplates as getDefaultTemplatesApi,
    saveDefaultTemplate as saveDefaultTemplateApi // new api end point
} from '../services/testService'
import Configuration from './Configuration';
import UserManagement from './UserManagement';
import BusinessManagement from './business/BusinessManagement';
import TemplateManagement from './TemplateManagement';
import StageManagement from './StageManagement';
import SendMessage from './SendMessage';

function MyInterface() {
    const [apiKey, setApiKey] = useState(localStorage.getItem('icmpApiKey') || '');
    const [userId, setUserId] = useState('');
    const [businessId, setBusinessId] = useState('');
    const [defaultTemplates, setDefaultTemplates] = React.useState([]);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [availableVariable, setAvailableVariable] = React.useState([]);
    const [selectedVariable, setSelectedVariable] = React.useState('');
    const [businessName, setBusinessName] = useState('');
    const [templateID, setTemplateID] = React.useState('');
    const [templateName, setTemplateName] = useState('');
    const [templateText, setTemplateText] = useState('');
    const [stageId, setStageId] = useState(''); // Stage ID for editing
    const [stageName, setStageName] = useState('');
    const [stageDescription, setStageDescription] = useState('');
    const [stageType, setStageType] = useState('');
    const [selectionTemplateId, setSelectionTemplateId] = useState('');
    const [selectionCustomPrompt, setSelectionCustomPrompt] = useState('');
    const [extractionTemplateId, setExtractionTemplateId] = useState('');
    const [extractionCustomPrompt, setExtractionCustomPrompt] = useState('');
    const [responseTemplateId, setResponseTemplateId] = useState('');
    const [responseCustomPrompt, setResponseCustomPrompt] = useState('');
    const [messageInput, setMessageInput] = useState('');

    const [configOutput, setConfigOutput] = useState('');
    const [userOutput, setUserOutput] = useState('');
    const [businessOutput, setBusinessOutput] = useState('');
    const [templateOutput, setTemplateOutput] = useState('');
    const [stageOutput, setStageOutput] = useState('');
    const [messageOutput, setMessageOutput] = useState('');

    // Snackbar
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // or 'error'

    // Open and close snackbar
    const handleSnackbarOpen = (message, severity) => {
        setSnackbarMessage(message);
        setSnackbarSeverity(severity);
        setSnackbarOpen(true);
    };

    const handleSnackbarClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setSnackbarOpen(false);
    };

    // Configuration
    const saveConfig = async () => {
        try {
            const response = await saveConfigApi(apiKey, userId, businessId)
            localStorage.setItem('icmpApiKey', apiKey);
            setConfigOutput(`Configuration Saved:\nUser ID: ${userId}\nBusiness ID: ${businessId}\nAPI Key: ${apiKey}`);
            handleSnackbarOpen("Configuration Saved!", "success")

        } catch (error) {
            setConfigOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    //user section
    const createUser = async () => {
        try {
            const response = await createUserApi(firstName, lastName, email)
            setUserOutput("User Created (dummy)");
            handleSnackbarOpen("User Created!", "success")

        } catch (error) {
            setUserOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")

        }
    };

    const fetchBusinessDetails = async () => {
        if (!businessId) {
            setBusinessOutput("Please enter a Business ID.");
            handleSnackbarOpen("Please enter a Business ID.", "warning")
            return;
        }
        try {
            const response = await fetchBusinessDetailsApi(businessId, apiKey)
            setBusinessOutput("Business endpoint not implemented yet.");
            handleSnackbarOpen("Business endpoint not implemented yet.", "info")

        } catch (error) {
            setBusinessOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")

        }
    };

    const createTemplate = async () => {
        const templateData = {
            template_name: templateName,
            template_text: templateText
        };
        try {
            const data = await createTemplateApi(templateData, apiKey)
            setTemplateOutput(`Template Created: ${data.template_id}`);
            handleSnackbarOpen(`Template Created: ${data.template_id}`, "success")
        } catch (error) {
            setTemplateOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")

        }
    };

    const fetchTemplates = async () => {
        try {
            const data = await fetchTemplatesApi(apiKey)
            setTemplateOutput(JSON.stringify(data, null, 2));
            handleSnackbarOpen("Templates Fetched!", "success")

        } catch (error) {
            setTemplateOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    const addVariableToTemplate = () => {
        // Combine the static and dynamic variables
        let newTemplateText = templateText + "{" + selectedVariable + "}";
        setTemplateText(newTemplateText);
    };

    const handleTemplateSelection = (event) => {
        const selectedTemplateId = event.target.value;
        setTemplateID(selectedTemplateId);
        // Find the selected template object
        const selectedTemplate = defaultTemplates.find(template => template.template_id === selectedTemplateId);

        // If the template is found, update the templateText state
        if (selectedTemplate) {
            setTemplateText(selectedTemplate.template_text);
        } else {
            setTemplateText(''); // Clear the template text if the template is not found
        }

    };

    const handleSaveDefaultTemplate = async () => {
        try {
            const templateData = {
                template_name: templateName,
                template_text: templateText
            };
            // const data = await createTemplateApi(templateData, apiKey)
            // await saveDefaultTemplateApi(templateData, apiKey); // Implement API call to save the current template to defaults
            setTemplateOutput(`Template Saved to Defaults: ${templateID}`);
            handleSnackbarOpen(`Template Saved to Defaults: ${templateID}`, "success");

        } catch (error) {
            handleSnackbarOpen(`Error saving template: ${error.message}`, "error");
        }
    };

    const handleVariableSelection = (event) => {
        setSelectedVariable(event.target.value);
    };
    //stage section
    const createStage = async () => {
        const stageData = {
            business_id: businessId,
            stage_name: stageName,
            stage_description: stageDescription,
            stage_type: stageType,
            selection_template_id: selectionTemplateId || null,
            selection_custom_prompt: selectionCustomPrompt || null,
            extraction_template_id: extractionTemplateId || null,
            extraction_custom_prompt: extractionCustomPrompt || null,
            response_template_id: responseTemplateId || null,
            response_custom_prompt: responseCustomPrompt || null
        };

        try {
            const data = await createStageApi(stageData, apiKey)
            setStageOutput(`Stage Created: ${data.stage_id}`);
            handleSnackbarOpen(`Stage Created: ${data.stage_id}`, "success")
        } catch (error) {
            setStageOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    const fetchStages = async () => {
        if (!businessId) {
            setStageOutput("Please enter a Business ID.");
            handleSnackbarOpen("Please enter a Business ID.", "warning");

            return;
        }
        try {
            const data = await fetchStagesApi(businessId, apiKey)
            setStageOutput(JSON.stringify(data, null, 2));
            handleSnackbarOpen("Stages Fetched!", "success")

        } catch (error) {
            setStageOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    const processMessage = async () => {
        const messageData = {
            business_id: businessId,
            user_id: userId,
            message: messageInput
        };
        try {
            const data = await processMessageApi(messageData, apiKey)
            setMessageOutput(`Response: ${data.response}\nConversation ID: ${data.conversation_id}`);
            handleSnackbarOpen(`Response: ${data.response}\nConversation ID: ${data.conversation_id}`, "success")

        } catch (error) {
            setMessageOutput(`Error: ${error.message}`);
            handleSnackbarOpen(error.message, "error")
        }
    };

    useEffect(() => {
        // When the app load, load the API KEY
        const storedApiKey = localStorage.getItem('icmpApiKey');
        if (storedApiKey) {
            setApiKey(storedApiKey);
        }
    }, []);

    return (
        <div className="container">
            <Typography variant="h4" align="center" gutterBottom>ICMP Proof of Concept</Typography>

            <Configuration apiKey={apiKey} setApiKey={setApiKey} userId={userId} setUserId={setUserId} businessId={businessId} setBusinessId={setBusinessId} handleSnackbarOpen={handleSnackbarOpen} />
            <UserManagement firstName={firstName} setFirstName={setFirstName} lastName={lastName} setLastName={setLastName} email={email} setEmail={setEmail} userOutput={userOutput} createUser={createUser} handleSnackbarOpen={handleSnackbarOpen} />
            <BusinessManagement businessName={businessName} setBusinessName={setBusinessName} businessOutput={businessOutput} fetchBusinessDetails={fetchBusinessDetails} handleSnackbarOpen={handleSnackbarOpen} />
            <TemplateManagement templateID={templateID} setTemplateID={setTemplateID} availableVariable={availableVariable} setAvailableVariable={setAvailableVariable} selectedVariable={selectedVariable} setSelectedVariable={setSelectedVariable} handleTemplateSelection={handleTemplateSelection} handleVariableSelection={handleVariableSelection} addVariableToTemplate={addVariableToTemplate} templateName={templateName} setTemplateName={setTemplateName} templateText={templateText} setTemplateText={setTemplateText} templateOutput={templateOutput} createTemplate={createTemplate} fetchTemplates={fetchTemplates} handleSnackbarOpen={handleSnackbarOpen} />
            <StageManagement stageId={stageId} setStageId={setStageId} stageName={stageName} setStageName={setStageName} stageDescription={stageDescription} setStageDescription={setStageDescription} stageType={stageType} setStageType={setStageType} selectionTemplateId={selectionTemplateId} setSelectionTemplateId={setSelectionTemplateId} selectionCustomPrompt={selectionCustomPrompt} setSelectionCustomPrompt={setSelectionCustomPrompt} extractionTemplateId={extractionTemplateId} setExtractionTemplateId={setExtractionTemplateId} extractionCustomPrompt={extractionCustomPrompt} setExtractionCustomPrompt={setExtractionCustomPrompt} responseTemplateId={responseTemplateId} setResponseTemplateId={setResponseTemplateId} responseCustomPrompt={responseCustomPrompt} setResponseCustomPrompt={setResponseCustomPrompt} stageOutput={stageOutput} createStage={createStage} updateStage={processMessage} fetchStages={fetchStages} handleSnackbarOpen={handleSnackbarOpen} />
            <SendMessage messageInput={messageInput} setMessageInput={setMessageInput} messageOutput={messageOutput} processMessage={processMessage} handleSnackbarOpen={handleSnackbarOpen} />

            {/* Snackbar for notifications */}
            <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose} anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}>
                <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </div>
    );
}

export default MyInterface;