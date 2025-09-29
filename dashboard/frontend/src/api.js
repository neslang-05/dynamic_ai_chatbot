// API configuration for GitHub Codespaces
const getApiBaseUrl = () => {
  // Check if we're in a codespace environment
  if (window.location.hostname.includes('.app.github.dev')) {
    // Extract codespace name and construct backend URL
    const frontendUrl = window.location.hostname;
    const backendUrl = frontendUrl.replace('-3000.app.github.dev', '-5000.app.github.dev');
    return `https://${backendUrl}`;
  }
  
  // Local development
  return process.env.REACT_APP_API_URL || 'http://localhost:5000';
};

const API_BASE_URL = getApiBaseUrl();
console.log('Dashboard API URL:', API_BASE_URL);

export const apiClient = {
  get: async (endpoint) => {
    try {
      console.log(`Fetching: ${API_BASE_URL}${endpoint}`);
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log(`Success: ${endpoint}`, data);
      return data;
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error.message);
      throw error;
    }
  }
};

export default apiClient;