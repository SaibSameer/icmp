// src/hooks/useTemplateManagement.js
import { useState, useCallback } from 'react';
import { fetchTemplates as fetchTemplatesApi } from '../services/testService';

const useTemplateManagement = (apiKey, handleSnackbarOpen) => {
    const [templateID, setTemplateID] = useState('');
    const [templateName, setTemplateName] = useState('');
    const [templateText, setTemplateText] = useState('');
    const [templateOutput, setTemplateOutput] = useState('');
    const [availableVariable, setAvailableVariable] = useState([]);
    const [selectedVariable, setSelectedVariable] = useState('');
    const [defaultTemplates, setDefaultTemplates] = useState([]);

    const loadTemplates = useCallback(async () => {
        try {
            const templates = await fetchTemplatesApi(apiKey);
            setDefaultTemplates(templates);
            setTemplateOutput("Templates Fetched!");
            handleSnackbarOpen("Templates Fetched!", "success");
        } catch (error) {
            setTemplateOutput(`Error fetching templates: ${error.message}`);
            handleSnackbarOpen(`Error fetching templates: ${error.message}`, "error");
        }
    }, [apiKey, handleSnackbarOpen]);

    const handleTemplateSelection = (event) => {
        const selectedTemplateId = event.target.value;
        setTemplateID(selectedTemplateId);
        const selectedTemplate = defaultTemplates.find(template => template.template_id === selectedTemplateId);

        if (selectedTemplate) {
            setTemplateText(selectedTemplate.template_text);
        } else {
            setTemplateText('');
        }
    };

    const handleVariableSelection = (event) => {
        setSelectedVariable(event.target.value);
    };

    const addVariableToTemplate = () => {
        let newTemplateText = templateText + "{" + selectedVariable + "}";
        setTemplateText(newTemplateText);
    };

    // useEffect to load templates when the component mounts
    // Add logic createTemplate and saveDefaultTemplate
    return {
        templateID,
        setTemplateID,
        templateName,
        setTemplateName,
        templateText,
        setTemplateText,
        templateOutput,
        setTemplateOutput,
        availableVariable,
        setAvailableVariable,
        selectedVariable,
        setSelectedVariable,
        addVariableToTemplate,
        handleTemplateSelection,
        handleVariableSelection,
        loadTemplates
    };
};

export default useTemplateManagement;