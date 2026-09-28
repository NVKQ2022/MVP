import apiClient from '@/services/api';

const WHITELIST_BASE_URL = '/api/v1/admin/whitelist';

export const whitelistApi = {

    // params: search (string), isActive (bool), page (int), pageSize (int)
    getAll: (params = {}) =>
        apiClient.get(WHITELIST_BASE_URL, { params }).then((res) => res.data),

    create: (payload) =>
        apiClient.post(WHITELIST_BASE_URL, payload).then((res) => res.data),

    getById: (id) =>
        apiClient.get(`${WHITELIST_BASE_URL}/${id}`).then((res) => res.data),

    update: ({ id, email, domain }) => {
        return apiClient.put(`${WHITELIST_BASE_URL}/${id}`, { email, domain }).then((res) => res.data);
    },

    remove: (id) =>
        apiClient.delete(`${WHITELIST_BASE_URL}/${id}`).then((res) => res.data),

    activate: (id) => apiClient.patch(`${WHITELIST_BASE_URL}/${id}/activate`).then((res) => res.data),
    deactivate: (id) => apiClient.patch(`${WHITELIST_BASE_URL}/${id}/deactivate`).then((res) => res.data),
};