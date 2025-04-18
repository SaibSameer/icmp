// File: src/components/MyInterface.js
// Last Modified: 2026-03-30
import React, { useState } from 'react';
import './MyInterface.css';
import { Typography, Snackbar, Alert } from '@mui/material';
import Configuration from './Configuration';
import BusinessSection from './BusinessSection';
import UserSection from './UserSection';
import SendMessage from './SendMessage';
import StageManagement from './StageManagement';
import useTemplateManagement from '../hooks/useTemplateManagement';
import useStageManagement from '../hooks/useStageManagement';
import useConfig from '../hooks/useConfig';
import useUser from '../hooks/useUser';
import { createUser as createUserApi, createTemplate as createTemplateApi } from '../services/testService';
import AgentSection from './AgentSection';
import StageSection from './StageSection';
import StageDetailView from './StageDetailView';
import TemplateSection from './TemplateSection';

// Main MyInterface component
function MyInterface() {
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // or 'error'
    const [selectedAgentId, setSelectedAgentId] = useState(null);
    const [selectedStageId, setSelectedStageId] = useState(null);

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

   const {
        apiKey,
        setApiKey,
        userId,
        setUserId,
        businessId,
        setBusinessId,
        businessApiKey,
        setBusinessApiKey,
    } = useConfig();

    const {
        firstName,
        setFirstName,
        lastName,
        setLastName,
        email,
        setEmail,
        userOutput,
        setUserOutput
    } = useUser();

    const {
        templateID,
        setTemplateID,
        templateName,
        setTemplateName,
        templateText,
        setTemplateText,
        templateOutput,
        setTemplateOutput,
    } = useTemplateManagement(apiKey, handleSnackbarOpen);

    const {
        stageId,
        setStageId,
        stageName,
        setStageName,
        stageDescription,
        setStageDescription,
        stageType,
        setStageType,
        selectionTemplateId,
        setSelectionTemplateId,
        selectionCustomPrompt,
        setSelectionCustomPrompt,
         extractionTemplateId,
        setExtractionTemplateId,
        extractionCustomPrompt,
        setExtractionCustomPrompt,
        responseTemplateId,
        setResponseTemplateId,
        responseCustomPrompt,
        setResponseCustomPrompt,
        stageOutput,
        setStageOutput,
        fetchStages,
        createStage
    } = useStageManagement(apiKey, businessId, handleSnackbarOpen);

    //user section
    const createUser = async () => {
        try {
            await createUserApi(firstName, lastName, email)
            setUserOutput("User Created (dummy)");
            handleSnackbarOpen("User Created!", "success")

        } catch (error) {
            setUserOutput(`Error: ${error.message}`);
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

    // Define placeholder processMessage function
    const processMessage = async (message) => {
        console.log("Processing message (TODO):", message);
        // TODO: Implement actual message processing logic, likely calling an API
        handleSnackbarOpen("Message processing not yet implemented.", "info");
    };

    // Handler for when an agent is selected in AgentSection
    const handleAgentSelect = (agentId) => {
        console.log("Agent selected in MyInterface:", agentId);
        setSelectedAgentId(agentId);
        // Clear stage selection when agent changes
        setSelectedStageId(null); 
    };

    // Handler for when a stage is selected in StageSection
    const handleStageSelect = (stageId) => {
        console.log("Stage selected in MyInterface:", stageId);
        setSelectedStageId(stageId);
    };

    // Determine if configuration is complete (we check for businessId as a proxy)
    const isConfigComplete = !!businessId && !!userId; // Check both IDs are present

    return (
        <div className="container">
            <Typography variant="h4" align="center" gutterBottom>ICMP Proof of Concept</Typography>

            {!isConfigComplete ? (
                <Configuration
                    apiKey={apiKey}
                    setApiKey={setApiKey}
                    userId={userId}
                    setUserId={setUserId}
                    businessId={businessId}
                    setBusinessId={setBusinessId}
                    businessApiKey={businessApiKey}
                    setBusinessApiKey={setBusinessApiKey}
                    handleSnackbarOpen={handleSnackbarOpen}
                />
            ) : (
                // Render dashboard content only if config is complete
                <>
                    <BusinessSection handleSnackbarOpen={handleSnackbarOpen} />

                    <AgentSection 
                        handleSnackbarOpen={handleSnackbarOpen} 
                        onAgentSelect={handleAgentSelect} 
                    />

                    <UserSection
                        firstName={firstName}
                        setFirstName={setFirstName}
                        lastName={lastName}
                        setLastName={setLastName}
                        email={email}
                        setEmail={setEmail}
                        createUser={createUser}
                        userOutput={userOutput}
                    />

                    <TemplateSection
                        templateID={templateID}
                        setTemplateID={setTemplateID}
                        templateName={templateName}
                        setTemplateName={setTemplateName}
                        templateText={templateText}
                        setTemplateText={setTemplateText}
                        createTemplate={createTemplate}
                        templateOutput={templateOutput}
                    />

                    <StageManagement
                        stageId={stageId}
                        setStageId={setStageId}
                        stageName={stageName}
                        setStageName={setStageName}
                        stageDescription={stageDescription}
                        setStageDescription={setStageDescription}
                        stageType={stageType}
                        setStageType={setStageType}
                        selectionTemplateId={selectionTemplateId}
                        setSelectionTemplateId={setSelectionTemplateId}
                        selectionCustomPrompt={selectionCustomPrompt}
                        setSelectionCustomPrompt={setSelectionCustomPrompt}
                         extractionTemplateId={extractionTemplateId}
                        setExtractionTemplateId={setExtractionTemplateId}
                        extractionCustomPrompt={extractionCustomPrompt}
                        setExtractionCustomPrompt={setExtractionCustomPrompt}
                        responseTemplateId={responseTemplateId}
                        setResponseTemplateId={setResponseTemplateId}
                        responseCustomPrompt={responseCustomPrompt}
                        setResponseCustomPrompt={setResponseCustomPrompt}
                        stageOutput={stageOutput}
                        setStageOutput={setStageOutput}
                        fetchStages={fetchStages}
                        createStage={createStage}
                        handleSnackbarOpen={handleSnackbarOpen}
                        apiKey={apiKey}
                        businessId={businessId} />

                    {/* Render StageSection, passing selectedAgentId and selection handler */}
                    <StageSection 
                        selectedAgentId={selectedAgentId} 
                        handleSnackbarOpen={handleSnackbarOpen}
                        onStageSelect={handleStageSelect}
                    />

                    {/* Conditionally render StageDetailView only when a stage is selected */}
                    {selectedStageId && (
                        <StageDetailView 
                            selectedStageId={selectedStageId} 
                            handleSnackbarOpen={handleSnackbarOpen} 
                        />
                    )}

                    <SendMessage processMessage={processMessage} handleSnackbarOpen={handleSnackbarOpen} />
                </>
            )}

            {/* Snackbar for notifications */}
            <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
                <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </div>
    );
}

export default MyInterface;