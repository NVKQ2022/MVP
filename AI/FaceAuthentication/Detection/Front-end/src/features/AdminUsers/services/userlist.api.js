import apiClient from '@/services/api';

const ADMIN_USERS_BASE_URL = '/api/v1/admin/users';

export const adminUsersApi = {
    getAll: (params = {}) =>
        apiClient.get(ADMIN_USERS_BASE_URL, { params }).then((res) => res.data),

    getById: (id) =>
        apiClient.get(`${ADMIN_USERS_BASE_URL}/${id}`).then((res) => res.data),

    update: ({ id, roleId }) => {
        return apiClient.put(`${ADMIN_USERS_BASE_URL}/${id}`, { roleId }).then((res) => res.data);
    },

    remove: (id) =>
        apiClient.delete(`${ADMIN_USERS_BASE_URL}/${id}`).then((res) => res.data),

    lock: (id) => apiClient.patch(`${ADMIN_USERS_BASE_URL}/${id}/lock`).then((res) => res.data),
    unlock: (id) => apiClient.patch(`${ADMIN_USERS_BASE_URL}/${id}/unlock`).then((res) => res.data),
    activate: (id) => apiClient.patch(`${ADMIN_USERS_BASE_URL}/${id}/activate`).then((res) => res.data),
};