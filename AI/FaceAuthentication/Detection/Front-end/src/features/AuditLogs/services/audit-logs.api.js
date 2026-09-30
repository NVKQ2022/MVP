import apiClient from '@/services/api';

const AUDIT_LOG_BASE_URL = '/api/v1/admin/audit-logs';

export const auditLogApi = {
  getAll: ({ action, entityType, dateFrom, dateTo, ...params } = {}) =>
    apiClient
      .get(AUDIT_LOG_BASE_URL, {
        params: {
          ...params,
          Action: action,
          EntityType: entityType,
          From: dateFrom,
          To: dateTo,
        },
      })
      .then((res) => res.data),

  getById: (id) =>
    apiClient.get(`${AUDIT_LOG_BASE_URL}/${id}`).then((res) => res.data),
};