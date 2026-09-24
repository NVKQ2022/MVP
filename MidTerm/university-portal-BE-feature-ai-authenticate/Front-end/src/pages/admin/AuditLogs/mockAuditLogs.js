// Mock data for Admin Audit Logs
// Replace this file's export with a real API call when the backend endpoint is ready.

export const AUDIT_ACTIONS = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT'];

export const AUDIT_STATUSES = ['SUCCESS', 'FAILED'];

export const AUDIT_USERS = [
  { id: 'u1', name: 'John Smith', email: 'j.smith@company.com' },
  { id: 'u2', name: 'Emily Johnson', email: 'e.johnson@company.com' },
  { id: 'u3', name: 'Michael Anderson', email: 'm.anderson@company.com' },
  { id: 'u4', name: 'Sarah Williams', email: 's.williams@company.com' },
];

const findUser = (id) => AUDIT_USERS.find((u) => u.id === id);

export const mockAuditLogs = [
  {
    id: 'log-001',
    timestamp: '2026-09-23T09:12:45Z',
    user: findUser('u1'),
    action: 'LOGIN',
    module: 'Auth',
    resourceId: '-',
    status: 'SUCCESS',
    ip: '10.0.0.14',
  },
  {
    id: 'log-002',
    timestamp: '2026-09-23T09:20:11Z',
    user: findUser('u2'),
    action: 'CREATE',
    module: 'Documents',
    resourceId: 'DOC-3391',
    status: 'SUCCESS',
    ip: '10.0.0.22',
  },
  {
    id: 'log-003',
    timestamp: '2026-09-23T09:31:02Z',
    user: findUser('u3'),
    action: 'UPDATE',
    module: 'Users',
    resourceId: 'USR-0044',
    status: 'SUCCESS',
    ip: '10.0.0.7',
  },
  {
    id: 'log-004',
    timestamp: '2026-09-23T10:02:58Z',
    user: findUser('u4'),
    action: 'DELETE',
    module: 'Documents',
    resourceId: 'DOC-3210',
    status: 'FAILED',
    ip: '10.0.0.31',
  },
  {
    id: 'log-005',
    timestamp: '2026-09-23T10:15:40Z',
    user: findUser('u1'),
    action: 'EXPORT',
    module: 'Reports',
    resourceId: 'RPT-0091',
    status: 'SUCCESS',
    ip: '10.0.0.14',
  },
  {
    id: 'log-006',
    timestamp: '2026-09-23T10:44:19Z',
    user: findUser('u2'),
    action: 'LOGOUT',
    module: 'Auth',
    resourceId: '-',
    status: 'SUCCESS',
    ip: '10.0.0.22',
  },
  {
    id: 'log-007',
    timestamp: '2026-09-22T14:05:03Z',
    user: findUser('u3'),
    action: 'UPDATE',
    module: 'Settings',
    resourceId: 'CFG-0002',
    status: 'FAILED',
    ip: '10.0.0.7',
  },
  {
    id: 'log-008',
    timestamp: '2026-09-22T15:30:27Z',
    user: findUser('u4'),
    action: 'CREATE',
    module: 'Users',
    resourceId: 'USR-0051',
    status: 'SUCCESS',
    ip: '10.0.0.31',
  },
  {
    id: 'log-009',
    timestamp: '2026-09-21T08:55:12Z',
    user: findUser('u1'),
    action: 'LOGIN',
    module: 'Auth',
    resourceId: '-',
    status: 'FAILED',
    ip: '10.0.0.14',
  },
  {
    id: 'log-010',
    timestamp: '2026-09-21T11:20:36Z',
    user: findUser('u2'),
    action: 'DELETE',
    module: 'Users',
    resourceId: 'USR-0033',
    status: 'SUCCESS',
    ip: '10.0.0.22',
  },
];