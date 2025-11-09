const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchWithError(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(data.error || 'Request failed', response.status);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error: ' + error.message, 0);
  }
}

export const api = {
  async getProducts() {
    return fetchWithError(`${API_BASE_URL}/api/products`);
  },

  async getProductDetails(productId) {
    return fetchWithError(`${API_BASE_URL}/api/products/${productId}/details`);
  },

  async getSuggestions(productId) {
    return fetchWithError(`${API_BASE_URL}/api/suggestions?product_id=${productId}`);
  },

  async applySuggestion(suggestionId) {
    return fetchWithError(`${API_BASE_URL}/api/suggestions/${suggestionId}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  },

  async getEvents(limit = 20) {
    return fetchWithError(`${API_BASE_URL}/api/events?limit=${limit}`);
  },

  async healthCheck() {
    return fetchWithError(`${API_BASE_URL}/health`);
  },

  // Store Connections
  async getConnections() {
    return fetchWithError(`${API_BASE_URL}/api/connections`);
  },

  async createConnection(connectionData) {
    return fetchWithError(`${API_BASE_URL}/api/connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connectionData),
    });
  },

  async deleteConnection(connectionId) {
    return fetchWithError(`${API_BASE_URL}/api/connections/${connectionId}`, {
      method: 'DELETE',
    });
  },

  async syncConnection(connectionId) {
    return fetchWithError(`${API_BASE_URL}/api/connections/${connectionId}/sync`, {
      method: 'POST',
    });
  },

  async quickDemoSetup() {
    return fetchWithError(`${API_BASE_URL}/api/connections/demo/quick-setup`, {
      method: 'POST',
    });
  },

  // AI Suggestions
  async generateSuggestionsForAll() {
    return fetchWithError(`${API_BASE_URL}/api/ai/analyze-all`, {
      method: 'POST',
    });
  },

  async generateSuggestionsForProduct(productId) {
    return fetchWithError(`${API_BASE_URL}/api/ai/analyze/${productId}`, {
      method: 'POST',
    });
  },
};
