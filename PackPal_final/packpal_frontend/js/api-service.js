/**
 * API Service for PackPal
 * This file contains utility functions to interact with the backend API
 */

// API base URL - change this to match your backend server address
const API_BASE_URL = 'http://localhost:8000';

// Ensure we have a token for testing - create one if needed
function ensureAuthToken() {
    let token = localStorage.getItem('authToken');
    if (!token) {
        token = 'test_token_' + Math.random().toString(36).substring(2);
        localStorage.setItem('authToken', token);
        console.log('Created new auth token for testing:', token);
    }
    return token;
}

// Call this once when the script loads
ensureAuthToken();

/**
 * Generic fetch function with error handling
 * @param {string} endpoint - API endpoint to call
 * @param {Object} options - Fetch options
 * @returns {Promise} - API response as JSON
 */
async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Add authorization header if token exists
    const token = ensureAuthToken();
    console.log(`Using auth token for ${endpoint}:`, token);
    headers['Authorization'] = `Bearer ${token}`;
    
    try {
        console.log(`Making ${options.method || 'GET'} request to ${url}`, options.body || '');
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        console.log(`Response status for ${endpoint}:`, response.status);
        
        // Read the response body text once and store it
        const responseText = await response.text();
        console.log(`Raw response for ${endpoint}:`, responseText);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            try {
                // Parse the already read text instead of calling response.json()
                const data = JSON.parse(responseText);
                
                // Log the response data
                console.log(`Response data for ${endpoint}:`, data);
                
                // If response is not ok, throw error with message
                if (!response.ok) {
                    throw new Error(data.message || data.error || `Error ${response.status}: ${response.statusText}`);
                }
                
                return data;
            } catch (parseError) {
                console.error('JSON parsing error:', parseError);
                console.error('Raw response:', responseText);
                throw new Error(`Failed to parse JSON response: ${parseError.message}`);
            }
        } else {
            if (!response.ok) {
                console.error('Non-JSON error response:', responseText);
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return responseText;
        }
    } catch (error) {
        console.error(`API Error for ${endpoint}:`, error);
        throw error;
    }
}

// Auth API
const AuthAPI = {
    login: async (email, password) => {
        return apiFetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },
    
    signup: async (userData) => {
        return apiFetch('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    logout: () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
    }
};

// Checklist API
const ChecklistAPI = {
    getAll: async () => {
        return apiFetch('/api/checklists');
    },
    
    getById: async (id) => {
        return apiFetch(`/api/checklists/${id}`);
    },
    
    create: async (checklist) => {
        return apiFetch('/api/checklists', {
            method: 'POST',
            body: JSON.stringify(checklist)
        });
    },
    
    update: async (id, checklist) => {
        return apiFetch(`/api/checklists/${id}`, {
            method: 'PUT',
            body: JSON.stringify(checklist)
        });
    },
    
    delete: async (id) => {
        return apiFetch(`/api/checklists/${id}`, {
            method: 'DELETE'
        });
    }
};

// Checklist Item API
const ChecklistItemAPI = {
    create: async (item) => {
        return apiFetch('/api/checklist-items', {
            method: 'POST',
            body: JSON.stringify(item)
        });
    },
    
    update: async (id, item) => {
        return apiFetch(`/api/checklist-items/${id}`, {
            method: 'PUT',
            body: JSON.stringify(item)
        });
    },
    
    delete: async (id) => {
        console.log(`Sending DELETE request for item ${id}`);
        try {
            const response = await apiFetch(`/api/checklist-items/${id}`, {
                method: 'DELETE'
            });
            console.log(`Successfully deleted item ${id}`, response);
            return response;
        } catch (error) {
            console.error(`Failed to delete item ${id}:`, error);
            throw error;
        }
    }
};

// Members API
const MembersAPI = {
    getAll: async () => {
        return apiFetch('/api/members');
    },
    
    getById: async (id) => {
        return apiFetch(`/api/members/${id}`);
    }
};

// Alerts API
const AlertsAPI = {
    getAll: async () => {
        return apiFetch('/api/alerts');
    },
    
    markAsRead: async (id) => {
        return apiFetch(`/api/alerts/${id}/read`, {
            method: 'PUT'
        });
    }
};

// Export all API services
window.API = {
    Auth: AuthAPI,
    Checklist: ChecklistAPI,
    ChecklistItem: ChecklistItemAPI,
    Members: MembersAPI,
    Alerts: AlertsAPI
}; 