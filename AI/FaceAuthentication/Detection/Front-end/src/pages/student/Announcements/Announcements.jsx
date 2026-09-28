import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable } from '@/components/common/DataTable';
import { AppPagination } from '@/components/common/AppPagination';
import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import { Input } from '@/components/ui/input/input';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { ListFilter, Search } from 'lucide-react';
import { useAnnouncementsQuery } from '@/features/StudentAnnouncement';

const PAGE_SIZE = 10;

const STATUS_LABEL = {
  true: { label: 'Viewed', variant: 'secondary' },
  false: { label: 'Not Viewed', variant: 'default' },
};

const STATUS_OPTIONS = [
  { value: 'viewed', label: 'Viewed' },
  { value: 'not_viewed', label: 'Not Viewed' },
];

const buildColumns = (onOpenDetail) => [
  {
    key: 'title',
    header: 'Title',
    render: (row) => (
      <span
        className="announcements__row-title announcements__row-title--clickable"
        role="button"
        tabIndex={0}
        onClick={() => onOpenDetail(row)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onOpenDetail(row);
          }
        }}
      >
        {row.title}
      </span>
    ),
  },
  {
    key: 'creatorName',
    header: 'Posted by',
  },
  {
    key: 'publishedAt',
    header: 'Published',
    render: (row) => (row.publishedAt ? new Date(row.publishedAt).toLocaleDateString('en-US') : '-'),
  },
  {
    key: 'isRead',
    header: 'Status',
    render: (row) => {
      const s = STATUS_LABEL[String(!!row.isRead)];
      return <Badge variant={s.variant}>{s.label}</Badge>;
    },
  },
];

const StudentAnnouncements = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(new Set());

  const { data, isLoading } = useAnnouncementsQuery({
    pageNumber: currentPage,
    pageSize: PAGE_SIZE,
    search: searchQuery.trim() || undefined,
    status: statusFilter.size > 0 ? Array.from(statusFilter) : undefined,
  });

  const items = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const toggleStatusValue = (value, checked) => {
    setStatusFilter((prev) => {
      const next = new Set(prev);
      checked ? next.add(value) : next.delete(value);
      return next;
    });
    setCurrentPage(1);
  };

  const handleOpenDetail = (row) => {
    navigate(`/announcements/${row.id}`);
  };

  const columns = buildColumns(handleOpenDetail);

  const activeFilterCount = statusFilter.size;

  return (
    <div className="announcements">
      <h2 className="announcements__title">Student Announcements</h2>

      <div className="announcements__toolbar">
        <div className="announcements__search">
          <Search className="announcements__search-icon" />
          <Input
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search announcements..."
            className="announcements__search-input"
          />
        </div>
      </div>

      <div className="announcements__filters">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <ListFilter className="announcements__btn-icon" />
              Status
              {statusFilter.size > 0 && (
                <Badge variant="secondary" className="announcements__filter-badge">
                  {statusFilter.size}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Filter by status</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {STATUS_OPTIONS.map((opt) => (
              <DropdownMenuCheckboxItem
                key={opt.value}
                checked={statusFilter.has(opt.value)}
                onCheckedChange={(checked) => toggleStatusValue(opt.value, checked)}
                onSelect={(e) => e.preventDefault()}
              >
                {opt.label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {activeFilterCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setStatusFilter(new Set());
              setCurrentPage(1);
            }}
          >
            Clear filters
          </Button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={items}
        rowKey={(row) => row.id}
        loading={isLoading}
        emptyMessage="No announcements found"
      />

      <AppPagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
};

export default StudentAnnouncements;