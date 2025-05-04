// File: src/components/MyInterface.js
// Last Modified: 2026-03-30
import React, { useState, useEffect } from 'react';
import './MyInterface.css';
import { Typography, Snackbar, Alert, CircularProgress } from '@mui/material';
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
import MessagePortal from './MessagePortal';

// Main MyInterface component
function MyInterface() {
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState('info');
    const [selectedStageId, setSelectedStageId] = useState(null);
    const [selectedAgentId, setSelectedAgentId] = useState(null);
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSnackbarOpen = (severity, message) => {
        setSnackbarSeverity(severity);
        setSnackbarMessage(message);
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

    const createUser = async () => {
        try {
            await createUserApi(firstName, lastName, email)
            setUserOutput("User Created (dummy)");
            handleSnackbarOpen("success", "User Created!");

        } catch (error) {
            setUserOutput(`Error: ${error.message}`);
            handleSnackbarOpen('error', error.message);

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
            handleSnackbarOpen('success', `Template Created: ${data.template_id}`);
        } catch (error) {
            setTemplateOutput(`Error: ${error.message}`);
            handleSnackbarOpen('error', error.message);

        }
    };

    const processMessage = async (message) => {
        console.log("Processing message (TODO):", message);
        handleSnackbarOpen('info', "Message processing not yet implemented.");
    };

    const handleAgentSelect = (agentId) => {
        console.log("Agent selected in MyInterface:", agentId);
        setSelectedAgentId(agentId);
        setSelectedStageId(null);
    };

    const handleStageSelect = (stageId) => {
        console.log("Stage selected in MyInterface:", stageId);
        setSelectedStageId(stageId);
    };

    const isConfigComplete = !!businessId && !!userId;

    const fetchConversations = async () => {
        setIsLoading(true);
        try {
            const response = await fetchConversationHistory();
            setConversations(response);
        } catch (error) {
            console.error('Error fetching conversations:', error);
            handleSnackbarOpen('error', 'Failed to fetch conversations');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchConversations();
    }, []);

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

                    <StageSection 
                        selectedAgentId={selectedAgentId} 
                        handleSnackbarOpen={handleSnackbarOpen}
                        onStageSelect={handleStageSelect}
                    />

                    {selectedStageId && (
                        <StageDetailView 
                            selectedStageId={selectedStageId} 
                            handleSnackbarOpen={handleSnackbarOpen} 
                        />
                    )}

                    <MessagePortal 
                        conversations={conversations}
                        isLoading={isLoading}
                        handleSnackbarOpen={handleSnackbarOpen}
                    />

                    <SendMessage 
                        handleSnackbarOpen={handleSnackbarOpen}
                        onMessageSent={fetchConversations}
                    />
                </>
            )}

            <Snackbar 
                open={snackbarOpen} 
                autoHideDuration={6000} 
                onClose={handleSnackbarClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            >
                <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </div>
    );
}

export default MyInterface;