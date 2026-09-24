import apiClient from '@/services/api';

const ANNOUNCEMENT_BASE_URL = '/api/v1/admin/announcements';

export const announcementApi = {
  getAll: (params = {}) =>
    apiClient.get(ANNOUNCEMENT_BASE_URL, { params }).then((res) => res.data),

  getById: (id) =>
    apiClient.get(`${ANNOUNCEMENT_BASE_URL}/${id}`).then((res) => res.data),

  create: (payload) =>
    apiClient.post(ANNOUNCEMENT_BASE_URL, payload).then((res) => res.data),

  update: ({ id, ...payload }) =>
    apiClient.put(`${ANNOUNCEMENT_BASE_URL}/${id}`, { id, ...payload }).then((res) => res.data),

  remove: (id) =>
    apiClient.delete(`${ANNOUNCEMENT_BASE_URL}/${id}`).then((res) => res.data),

  publish: (id) =>
    apiClient.patch(`${ANNOUNCEMENT_BASE_URL}/${id}/publish`).then((res) => res.data),

  archive: (id) =>
    apiClient.patch(`${ANNOUNCEMENT_BASE_URL}/${id}/archive`).then((res) => res.data),
};