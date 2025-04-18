// src/hooks/useStageManagement.js
import { useState } from 'react';
import { fetchStages as fetchStagesApi, createStage as createStageApi} from '../services/testService';

const useStageManagement = (apiKey, businessId, handleSnackbarOpen) => {
    const [stageId, setStageId] = useState('');
    const [stageName, setStageName] = useState('');
    const [stageDescription, setStageDescription] = useState('');
    const [stageType, setStageType] = useState('');
    const [selectionTemplateId, setSelectionTemplateId] = useState('');
    const [selectionCustomPrompt, setSelectionCustomPrompt] = useState('');
    const [extractionTemplateId, setExtractionTemplateId] = useState('');
    const [extractionCustomPrompt, setExtractionCustomPrompt] = useState('');
    const [responseTemplateId, setResponseTemplateId] = useState('');
    const [responseCustomPrompt, setResponseCustomPrompt] = useState('');
    const [stageOutput, setStageOutput] = useState('');

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

    return {
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
    };
};

export default useStageManagement;