import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
}

// Dev mode bypass: add ?dev=true to URL to auto-authenticate
const isDevBypass = new URLSearchParams(window.location.search).has('dev');
if (isDevBypass && !localStorage.getItem('mc_token')) {
  localStorage.setItem('mc_token', 'dev-token');
  localStorage.setItem('mc_user', JSON.stringify({ id: '1', email: 'dev@memorychat.io', full_name: 'Dev User' }));
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('mc_token'),
  user: JSON.parse(localStorage.getItem('mc_user') || 'null'),
  isAuthenticated: !!localStorage.getItem('mc_token'),
  
  login: (token: string, user: User) => {
    localStorage.setItem('mc_token', token);
    localStorage.setItem('mc_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('mc_token');
    localStorage.removeItem('mc_user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  setToken: (token: string) => {
    localStorage.setItem('mc_token', token);
    set({ token, isAuthenticated: true });
  },

  setUser: (user: User) => {
    localStorage.setItem('mc_user', JSON.stringify(user));
    set({ user });
  },
}));
