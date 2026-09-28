import { useQuery } from '@tanstack/react-query';
import { auditLogApi } from '@/features/AuditLogs';

export const auditLogKeys = {
  all: ['audit-logs'],
  lists: () => [...auditLogKeys.all, 'list'],
  list: (params) => [...auditLogKeys.lists(), params],
  details: () => [...auditLogKeys.all, 'detail'],
  detail: (id) => [...auditLogKeys.details(), id],
};

export const useAuditLogsQuery = (params = { pageNumber: 1, pageSize: 10 }) => {
  return useQuery({
    queryKey: auditLogKeys.list(params),
    queryFn: () => auditLogApi.getAll(params),
  });
}

export const useAuditLogQuery = (id) => {
  return useQuery({
    queryKey: auditLogKeys.detail(id),
    queryFn: () => auditLogApi.getById(id),
    enabled: Boolean(id),
  });
}