import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nlams_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nlams_access_token');
      localStorage.removeItem('nlams_refresh_token');
      localStorage.removeItem('nlams_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
