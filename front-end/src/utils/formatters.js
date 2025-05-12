/**
 * Format a date string to a readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
};

/**
 * Format duration in milliseconds to a readable format
 * @param {number} durationMs - Duration in milliseconds
 * @returns {string} Formatted duration string
 */
export const formatDuration = (durationMs) => {
    if (!durationMs) return 'N/A';
    
    const seconds = Math.floor(durationMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
};

/**
 * Format cost to a readable format
 * @param {number} cost - Cost value
 * @returns {string} Formatted cost string
 */
export const formatCost = (cost) => {
    if (!cost) return 'N/A';
    return `$${cost.toFixed(4)}`;
};

/**
 * Truncate text to a specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}; 