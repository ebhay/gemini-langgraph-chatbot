import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/signup', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

export const chatAPI = {
  sendMessage: (data: { user_input: string; session_id: string }) =>
    api.post('/api/chat', data),
  getSessions: () => api.get('/api/sessions'),
  getSessionHistory: (sessionId: string) =>
    api.get(`/api/sessions/${sessionId}`),
  deleteSession: (sessionId: string) =>
    api.delete(`/api/sessions/${sessionId}`),
  getProfile: () => api.get('/api/profile'),
  updateProfile: (data: { key: string; value: string }) =>
    api.post('/api/profile', data),
  getNotifications: () => api.get('/api/notifications'),
  markNotificationRead: (id: number) =>
    api.post(`/api/notifications/read/${id}`),
  deleteNotification: (id: number) =>
    api.delete(`/api/notifications/${id}`),
};

export default api;
