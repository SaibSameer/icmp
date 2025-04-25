// File: src/services/testService.js
// Last Modified: 2026-03-29
import axios from 'axios';
import { API_CONFIG } from '../config';
import { getAuthHeaders } from './authService';

// Helper function to handle API calls and error responses
const handleApiCall = async (url, method, data = null) => {
    const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
    };

    try {
        const response = await axios({
            method: method,
            url: url,
            headers: headers,
            data: data,
            withCredentials: true
        });

        if (response.status >= 200 && response.status < 300) {
            return response.data;
        } else {
            console.error("API call failed:", response);
            throw new Error(`API call failed with status ${response.status}`);
        }
    } catch (error) {
        console.error("API call failed:", error);
        throw error; // Re-throw the error for the component to handle
    }
};

// --------------------------------------------------------
// Configuration Service (Saving to localStorage - Insecure)
// --------------------------------------------------------
export const saveConfig = async (apiKey, userId, businessId, businessApiKey) => {
    // This function doesn't actually call an API. It only saves to localStorage.
    return new Promise((resolve) => {
        localStorage.setItem('icmpApiKey', apiKey);
        localStorage.setItem('userId', userId);
        localStorage.setItem('businessId', businessId);
        localStorage.setItem('businessApiKey', businessApiKey);
        resolve({ success: true, message: 'Configuration saved to localStorage' });
    });
};

// --------------------------------------------------------
// User Management Service (Simulated)
// --------------------------------------------------------
export const createUser = async (firstName, lastName, email) => {
    try {
        return await handleApiCall(`/users`, 'POST', {
            firstName,
            lastName,
            email
        });
    } catch (error) {
        console.error("createUser API call failed:", error);
        throw error;
    }
};

// --------------------------------------------------------
// Business Management Service
// --------------------------------------------------------
export const fetchBusinessDetails = async (businessId) => {
    try {
        return await handleApiCall(`/businesses/${businessId}`, 'GET');
    } catch (error) {
        console.error("fetchBusinessDetails API call failed:", error);
        throw error;
    }
};

// --------------------------------------------------------
// Template Management Service
// --------------------------------------------------------
export const createTemplate = async (templateData) => {
    try {
        return await handleApiCall(`/templates`, 'POST', templateData);
    } catch (error) {
        console.error("createTemplate API call failed:", error);
        throw error;
    }
};

export const fetchTemplates = async () => {
    try {
        return await handleApiCall(`/templates/defaultTemplates`, 'GET');
    } catch (error) {
        console.error("fetchTemplates API call failed:", error);
        throw error;
    }
};

// --------------------------------------------------------
// Stage Management Service
// --------------------------------------------------------
export const createStage = async (stageData) => {
    try {
        const API_ENDPOINT = `/stages`;
        return await handleApiCall(API_ENDPOINT, 'POST', stageData);
    } catch (error) {
        console.error("createStage API call failed:", error);
        throw error;
    }
};

export const fetchStages = async (businessId) => {
    try {
        const API_ENDPOINT = `/stages`;
        return await handleApiCall(API_ENDPOINT, 'GET');
    } catch (error) {
        console.error("fetchStages API call failed:", error);
        throw error;
    }
};

// --------------------------------------------------------
// Message Handling Service
// --------------------------------------------------------
export const processMessage = async (messageData) => {
    try {
        return await handleApiCall(`/message`, 'POST', messageData);
    } catch (error) {
        console.error("processMessage API call failed:", error);
        throw error;
    }
};

// --------------------------------------------------------
// defaultTemplates Management Service
// --------------------------------------------------------
export const getDefaultTemplates = async () => {
    try {
        return await handleApiCall(`/templates/defaultTemplates`, 'GET');
    } catch (error) {
        console.error("getDefaultTemplates API call failed:", error);
        throw error;
    }
};

export const saveDefaultTemplate = async (templateData) => {
    try {
        return await handleApiCall(`/templates/defaultTemplates`, 'POST', templateData);
    } catch (error) {
        console.error("saveDefaultTemplate API call failed:", error);
        throw error;
    }
};

export const getStage = async (stageId) => {
    try {
        return await handleApiCall(`/stage/${stageId}`, 'GET');
    } catch (error) {
        console.error("getStage API call failed:", error);
        throw error;
    }
};

export const updateStage = async (stageId, stageData) => {
    try {
        return await handleApiCall(`/stage/${stageId}`, 'PUT', stageData);
    } catch (error) {
        console.error("updateStage API call failed:", error);
        throw error;
    }
};