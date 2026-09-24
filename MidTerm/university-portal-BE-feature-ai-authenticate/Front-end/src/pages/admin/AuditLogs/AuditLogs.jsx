import { useMemo, useState } from 'react';
import { DataTable } from '@/components/common/DataTable';
import { Input } from '@/components/ui/input/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import { Badge } from '@/components/ui/badge/badge';
import { mockAuditLogs, AUDIT_ACTIONS, AUDIT_USERS } from './mockAuditLogs';

const ACTION_BADGE_VARIANT = {
  CREATE: 'default',
  UPDATE: 'secondary',
  DELETE: 'destructive',
  LOGIN: 'outline',
  LOGOUT: 'outline',
  EXPORT: 'secondary',
};

const STATUS_BADGE_VARIANT = {
  SUCCESS: 'default',
  FAILED: 'destructive',
};

const ALL_VALUE = 'ALL';

function formatTimestamp(iso) {
  return new Date(iso).toLocaleString('en-US', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function AdminAuditLogs() {
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState(ALL_VALUE);
  const [userFilter, setUserFilter] = useState(ALL_VALUE);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const filteredData = useMemo(() => {
    const query = search.trim().toLowerCase();

    return mockAuditLogs.filter((log) => {
      if (actionFilter !== ALL_VALUE && log.action !== actionFilter) return false;
      if (userFilter !== ALL_VALUE && log.user?.id !== userFilter) return false;

      if (dateFrom && new Date(log.timestamp) < new Date(dateFrom)) return false;
      if (dateTo && new Date(log.timestamp) > new Date(`${dateTo}T23:59:59`)) return false;

      if (query) {
        const haystack = [
          log.user?.name,
          log.user?.email,
          log.action,
          log.module,
          log.resourceId,
          log.ip,
        ]
          .join(' ')
          .toLowerCase();
        if (!haystack.includes(query)) return false;
      }

      return true;
    });
  }, [search, actionFilter, userFilter, dateFrom, dateTo]);

  const columns = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (row) => formatTimestamp(row.timestamp),
    },
    {
      key: 'user',
      header: 'User',
      render: (row) => (
        <div className="audit-logs__user-cell">
          <span className="audit-logs__user-name">{row.user?.name}</span>
          <span className="audit-logs__user-email">{row.user?.email}</span>
        </div>
      ),
    },
    {
      key: 'action',
      header: 'Action',
      render: (row) => (
        <Badge variant={ACTION_BADGE_VARIANT[row.action] ?? 'outline'}>{row.action}</Badge>
      ),
    },
    { key: 'module', header: 'Module' },
    { key: 'resourceId', header: 'Resource ID' },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={STATUS_BADGE_VARIANT[row.status] ?? 'outline'}>
          {row.status === 'SUCCESS' ? 'Success' : 'Failed'}
        </Badge>
      ),
    },
    { key: 'ip', header: 'IP' },
  ];

  return (
    <div className="audit-logs">
      <div className="audit-logs__header">
        <h1 className="audit-logs__title">Audit Logs</h1>
        <p className="audit-logs__subtitle">View the system's activity history</p>
      </div>

      <div className="audit-logs__filters">
        <div className="audit-logs__search-row">
          <Input
            className="audit-logs__search"
            placeholder="Search by user, module, resource ID, IP..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="audit-logs__filter-row">
          <div className="audit-logs__filter-item">
            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger className="audit-logs__filter-control">
                <SelectValue placeholder="Action" />
              </SelectTrigger>
              <SelectContent className="audit-logs__select-content">
                <SelectItem value={ALL_VALUE}>All actions</SelectItem>
                {AUDIT_ACTIONS.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="audit-logs__filter-item">
            <Select value={userFilter} onValueChange={setUserFilter}>
              <SelectTrigger className="audit-logs__filter-control">
                <SelectValue placeholder="User" />
              </SelectTrigger>
              <SelectContent className="audit-logs__select-content">
                <SelectItem value={ALL_VALUE}>All users</SelectItem>
                {AUDIT_USERS.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="audit-logs__date-range">
            <Input
              type="date"
              className="audit-logs__filter-control"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
            <span className="audit-logs__date-separator">–</span>
            <Input
              type="date"
              className="audit-logs__filter-control"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredData}
        rowKey={(row) => row.id}
        emptyMessage="No matching logs found"
      />
    </div>
  );
}