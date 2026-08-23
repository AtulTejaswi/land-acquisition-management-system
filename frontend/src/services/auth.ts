import api from './api';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role_name: string;
  state_id: string | null;
  state_name: string | null;
  district_id: string | null;
  district_name: string | null;
  agency_name: string | null;
  is_active: boolean;
}

export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const { data } = await api.post('/auth/login', { email, password });
    return data;
  },
  getMe: async (): Promise<User> => {
    const { data } = await api.get('/auth/me');
    return data;
  },
  forgotPassword: async (email: string) => {
    const { data } = await api.post('/auth/forgot-password', { email });
    return data;
  },
  logout: () => {
    localStorage.removeItem('nlams_access_token');
    localStorage.removeItem('nlams_refresh_token');
    localStorage.removeItem('nlams_user');
  },
};
