import apiClient from '@/services/api';

const ANNOUNCEMENT_BASE_URL = '/api/v1/announcements';

export const announcementApi = {
  getAll: (params = {}) =>
    apiClient.get(ANNOUNCEMENT_BASE_URL, { params }).then((res) => res.data),

  getById: (id) =>
    apiClient.get(`${ANNOUNCEMENT_BASE_URL}/${id}`).then((res) => res.data),
};