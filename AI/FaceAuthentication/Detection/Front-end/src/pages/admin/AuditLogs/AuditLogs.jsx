import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable } from '@/components/common/DataTable';
import { AppPagination } from '@/components/common/AppPagination';
import { Input } from '@/components/ui/input/input';
import { Badge } from '@/components/ui/badge/badge';
import { ErrorState } from '@/components/common/ErrorState';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import { useAuditLogsQuery } from '@/features/AuditLogs';
import AuditLogs from '.';

const PAGE_SIZE = 10;
const ALL_VALUE = 'ALL';

// Full set of `action` enum values per backend swagger.
const ACTION_OPTIONS = [
  'EntityCreated',
  'EntityUpdated',
  'EntityDeleted',
  'UserCreated',
  'UserUpdated',
  'UserDeleted',
  'UserLocked',
  'UserUnlocked',
  'UserActivated',
  'EmailVerified',
  'MfaEnabled',
  'LoginSuccess',
  'LoginFailed',
  'Logout',
  'RefreshTokenRotated',
  'AnnouncementCreated',
  'AnnouncementUpdated',
  'AnnouncementPublished',
  'AnnouncementArchived',
  'AnnouncementDeleted',
];

// Full set of `entityType` enum values per backend swagger.
const ENTITY_TYPE_OPTIONS = ['Announcement', 'User', 'EmailWhitelist', 'RefreshToken'];

const ACTION_BADGE_VARIANT = {
  EntityCreated: 'default',
  EntityUpdated: 'secondary',
  EntityDeleted: 'destructive',
};

function formatTimestamp(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('en-US', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const AdminAuditLogs = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState(ALL_VALUE);
  const [entityType, setEntityType] = useState(ALL_VALUE);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const { data, isLoading, isError, refetch } = useAuditLogsQuery({
    pageNumber: currentPage,
    pageSize: PAGE_SIZE,
    search: search.trim() || undefined,
    action: actionFilter !== ALL_VALUE ? actionFilter : undefined,
    entityType: entityType !== ALL_VALUE ? entityType : undefined,
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
  });

  const items = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setCurrentPage(1);
  };

  const handleActionFilterChange = (value) => {
    setActionFilter(value);
    setCurrentPage(1);
  };

  const handleEntityTypeChange = (value) => {
    setEntityType(value);
    setCurrentPage(1);
  };

  const handleDateFromChange = (e) => {
    setDateFrom(e.target.value);
    setCurrentPage(1);
  };

  const handleDateToChange = (e) => {
    setDateTo(e.target.value);
    setCurrentPage(1);
  };

  const handleRowClick = (row) => {
    navigate(`/audit-log/${row.id}`);
  };

  const withRowClick = (render) => (row) => (
    <div className="audit-logs__clickable-cell" onClick={() => handleRowClick(row)}>
      {render(row)}
    </div>
  );

  const columns = [
    {
      key: 'createdAt',
      header: 'Timestamp',
      render: withRowClick((row) => formatTimestamp(row.createdAt)),
    },
    {
      key: 'user',
      header: 'User',
      render: withRowClick((row) => (
        <div className="audit-logs__user-cell">
          <span className="audit-logs__user-name">{row.userName}</span>
          <span className="audit-logs__user-email">{row.userEmail}</span>
        </div>
      )),
    },
    {
      key: 'action',
      header: 'Action',
      render: withRowClick((row) => (
        <Badge variant={ACTION_BADGE_VARIANT[row.action] ?? 'outline'}>{row.action}</Badge>
      )),
    },
    {
      key: 'entityType',
      header: 'Entity Type',
      render: withRowClick((row) => row.entityType),
    },
    {
      key: 'entityId',
      header: 'Entity ID',
      render: withRowClick((row) => row.entityId),
    },
    {
      key: 'ipAddress',
      header: 'IP Address',
      render: withRowClick((row) => row.ipAddress),
    },
  ];

  if (isError) {
    return (
      <div className="audit-logs">
        <div className="audit-logs__header">
          <h1 className="audit-logs__title">Audit Logs</h1>
          <p className="audit-logs__subtitle">View the system's activity history</p>
        </div>
        <ErrorState
          title="Failed to load audit logs"
          description="We couldn't load the audit logs. Please try again."
          onRetry={refetch}
        />
      </div>
    );
  }

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
            placeholder="Search by user, entity, IP..."
            value={search}
            onChange={handleSearchChange}
          />
        </div>

        <div className="audit-logs__filter-row">
          <div className="audit-logs__filter-item">
            <Select value={actionFilter} onValueChange={handleActionFilterChange}>
              <SelectTrigger className="audit-logs__filter-control">
                <SelectValue placeholder="Action" />
              </SelectTrigger>
              <SelectContent className="audit-logs__select-content">
                <SelectItem value={ALL_VALUE}>All actions</SelectItem>
                {ACTION_OPTIONS.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="audit-logs__filter-item">
            <Select value={entityType} onValueChange={handleEntityTypeChange}>
              <SelectTrigger className="audit-logs__filter-control">
                <SelectValue placeholder="Entity type" />
              </SelectTrigger>
              <SelectContent className="audit-logs__select-content">
                <SelectItem value={ALL_VALUE}>All entity types</SelectItem>
                {ENTITY_TYPE_OPTIONS.map((entity) => (
                  <SelectItem key={entity} value={entity}>
                    {entity}
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
              onChange={handleDateFromChange}
            />
            <span className="audit-logs__date-separator">–</span>
            <Input
              type="date"
              className="audit-logs__filter-control"
              value={dateTo}
              onChange={handleDateToChange}
            />
          </div>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={items}
        rowKey={(row) => row.id}
        loading={isLoading}
        emptyMessage="No matching logs found"
      />

      <AppPagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} />
    </div>
  );
}

export default AdminAuditLogs;