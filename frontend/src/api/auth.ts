import { apiClient } from './client';

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/login', { email, password });
      return response.data;
    } catch (error: any) {
      throw error.response?.data?.detail || error.message || 'Login failed';
    }
  },

  register: async (email: string, password: string, fullName: string): Promise<UserResponse> => {
    try {
      const response = await apiClient.post<UserResponse>('/auth/register', {
        email,
        password,
        full_name: fullName,
      });
      return response.data;
    } catch (error: any) {
      throw error.response?.data?.detail || error.message || 'Registration failed';
    }
  },

  getMe: async (): Promise<UserResponse> => {
    try {
      const response = await apiClient.get<UserResponse>('/auth/me');
      return response.data;
    } catch (error: any) {
      throw error.response?.data?.detail || error.message || 'Failed to fetch user';
    }
  },

  logout: () => {
    localStorage.removeItem('mc_token');
    localStorage.removeItem('mc_user');
  },
};
