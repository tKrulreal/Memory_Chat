import axios from 'axios';

// Shared Axios instance with base config
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor — auto-attach Bearer token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mc_token');
    if (token && token !== 'dev-token') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle 401 → redirect to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data
      localStorage.removeItem('mc_token');
      localStorage.removeItem('mc_user');
      
      // Redirect to login (avoid redirect loop if already on login)
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
