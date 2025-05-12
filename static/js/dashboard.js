// Dashboard JavaScript

// Constants
const REFRESH_INTERVAL = 300000; // 5 minutes
const API_ENDPOINTS = {
    overview: '/api/dashboard/overview',
    trends: '/api/dashboard/trends',
    patterns: '/api/dashboard/patterns',
    errors: '/api/dashboard/errors',
    templates: '/api/dashboard/templates',
    all: '/api/dashboard/all'
};

// State management
let dashboardState = {
    lastUpdate: null,
    error: null,
    loading: false
};

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(num);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Error handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.insertBefore(errorDiv, document.body.firstChild);
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    document.body.insertBefore(successDiv, document.body.firstChild);
    successDiv.style.display = 'block';
    
    setTimeout(() => {
        successDiv.style.display = 'none';
        successDiv.remove();
    }, 3000);
}

// Loading state management
function setLoading(loading) {
    dashboardState.loading = loading;
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = loading ? 'flex' : 'none';
}

// Data fetching
async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching data from ${endpoint}:`, error);
        showError(`Error loading data: ${error.message}`);
        throw error;
    }
}

// Data processing
function processOverviewData(data) {
    return {
        total_extractions: formatNumber(data.total_extractions),
        success_rate: formatPercentage(data.success_rate),
        total_patterns: formatNumber(data.total_patterns),
        high_confidence: formatNumber(data.high_confidence_patterns)
    };
}

// Plot configuration
const plotConfig = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['sendDataToCloud', 'editInChartStudio'],
    toImageButtonOptions: {
        format: 'png',
        filename: 'dashboard-plot',
        height: 500,
        width: 700,
        scale: 2
    }
};

// Plot creation
function createTrendsPlot(data) {
    const trendData = JSON.parse(data.trend_plot);
    Plotly.newPlot('trends-plot', trendData.data, trendData.layout, plotConfig);
}

function createPatternsPlot(data) {
    const patternData = JSON.parse(data.pattern_plot);
    Plotly.newPlot('patterns-plot', patternData.data, patternData.layout, plotConfig);
}

function createErrorsPlot(data) {
    const errorData = JSON.parse(data.error_plot);
    Plotly.newPlot('errors-plot', errorData.data, errorData.layout, plotConfig);
}

function createTemplatesPlot(data) {
    const templateData = JSON.parse(data.template_plot);
    Plotly.newPlot('templates-plot', templateData.data, templateData.layout, plotConfig);
}

// Update UI
function updateOverview(data) {
    const processedData = processOverviewData(data);
    Object.entries(processedData).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = value;
        }
    });
}

function updateLastUpdateTime() {
    const now = new Date();
    dashboardState.lastUpdate = now;
    const timeElement = document.getElementById('last-update');
    if (timeElement) {
        timeElement.textContent = `Last updated: ${formatDate(now)}`;
    }
}

// Main dashboard update function
async function updateDashboard() {
    if (dashboardState.loading) return;
    
    setLoading(true);
    try {
        const data = await fetchData(API_ENDPOINTS.all);
        
        updateOverview(data.overview);
        createTrendsPlot(data.performance_trends);
        createPatternsPlot(data.pattern_analysis);
        createErrorsPlot(data.error_analysis);
        createTemplatesPlot(data.template_performance);
        
        updateLastUpdateTime();
        showSuccess('Dashboard updated successfully');
    } catch (error) {
        console.error('Error updating dashboard:', error);
    } finally {
        setLoading(false);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    updateDashboard();
    
    // Set up refresh interval
    setInterval(updateDashboard, REFRESH_INTERVAL);
    
    // Manual refresh button
    const refreshButton = document.querySelector('.refresh-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', updateDashboard);
    }
    
    // Add keyboard shortcut for refresh (Ctrl/Cmd + R)
    document.addEventListener('keydown', (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            updateDashboard();
        }
    });
});

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatNumber,
        formatPercentage,
        formatDate,
        processOverviewData,
        updateDashboard
    };
}