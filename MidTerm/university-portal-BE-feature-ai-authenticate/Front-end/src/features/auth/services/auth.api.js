import apiClient from '@/services/api';

export const authApi = {
  login: (credentials) => apiClient.post('/api/v1/Auth/login', credentials).then((res) => res.data),
  faceLogin: (formData) =>
    apiClient
      .post('/api/v1/Auth/face-login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((res) => res.data),
  register: (payload) => apiClient.post('/api/v1/Auth/register', payload).then((res) => res.data),
  refresh: (refreshToken) =>
    apiClient.post('/api/v1/Auth/refresh', { refreshToken }).then((res) => res.data),
  verifyEmail: (payload) =>
    apiClient.post('/api/v1/Auth/verify-email', payload).then((res) => res.data),
  logout: (refreshToken) =>
    apiClient.post('/api/v1/Auth/logout', { refreshToken }).then((res) => res.data),
};
