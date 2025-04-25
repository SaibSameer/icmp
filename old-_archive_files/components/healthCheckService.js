const API_KEY = 'YOUR_API_KEY'; // Replace with your actual API key
const API_ENDPOINT = '/health'; // Replace with your API endpoint if different

export const getHealthCheck = async () => {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'  // Ensure Content-Type is set
      }
    });

    if (!response.ok) {
      const errorData = await response.json(); // Try to get error message from API
      const errorMessage = errorData.message || `HTTP error! Status: ${response.status}`;
      throw new Error(errorMessage); // Throw the API's error message
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching health check:", error);
    throw error; // Re-throw the error for the component to handle
  }
};