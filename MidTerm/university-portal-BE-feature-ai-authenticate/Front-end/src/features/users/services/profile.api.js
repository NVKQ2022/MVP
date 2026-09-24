import apiClient from '@/services/api';

export const profileApi = {
  getMe: () => apiClient.get('/api/v1/users/me').then((res) => res.data),
  updateMe: (payload) => apiClient.put('/api/v1/users/me', payload).then((res) => res.data),
};
