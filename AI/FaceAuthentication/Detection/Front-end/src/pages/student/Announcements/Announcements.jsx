import { useMemo, useState } from 'react';
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
import { CheckCircle2, ListFilter, Search, Trash2 } from 'lucide-react';
import { announcementsData } from '@/data/announcementsData';

const PAGE_SIZE = 5;

const PRIORITY_LABEL = {
  high: { label: 'High', variant: 'destructive' },
  medium: { label: 'Medium', variant: 'default' },
  low: { label: 'Low', variant: 'secondary' },
};

const VIEWED_LABEL = {
  true: { label: 'Viewed', variant: 'secondary' },
  false: { label: 'Not Viewed', variant: 'default' },
};

// Filter option lists
const PRIORITY_OPTIONS = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const STATUS_OPTIONS = [
  { value: 'viewed', label: 'Viewed' },
  { value: 'not_viewed', label: 'Not Viewed' },
];

const columns = [
  {
    key: 'title',
    header: 'Title',
    render: (row) => <span className="announcements__row-title">{row.title}</span>,
  },
  {
    key: 'category',
    header: 'Category',
  },
  {
    key: 'author',
    header: 'Posted by',
  },
  {
    key: 'postedDate',
    header: 'Posted on',
    render: (row) => new Date(row.postedDate).toLocaleDateString('en-US'),
  },
  {
    key: 'priority',
    header: 'Priority',
    render: (row) => {
      const p = PRIORITY_LABEL[row.priority] ?? { label: row.priority, variant: 'default' };
      return <Badge variant={p.variant}>{p.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const v = VIEWED_LABEL[String(!!row.viewed)];
      return <Badge variant={v.variant}>{v.label}</Badge>;
    },
  },
];

const StudentAnnouncements = ({
  data = announcementsData,
  loading = false,
  onMarkViewed,
  onDelete,
}) => {
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState(new Set());
  const [statusFilter, setStatusFilter] = useState(new Set());

  const filteredData = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return data.filter((row) => {
      const matchesSearch =
        !query ||
        row.title?.toLowerCase().includes(query) ||
        row.category?.toLowerCase().includes(query) ||
        row.author?.toLowerCase().includes(query);

      const matchesPriority = priorityFilter.size === 0 || priorityFilter.has(row.priority);

      const statusValue = row.viewed ? 'viewed' : 'not_viewed';
      const matchesStatus = statusFilter.size === 0 || statusFilter.has(statusValue);

      return matchesSearch && matchesPriority && matchesStatus;
    });
  }, [data, searchQuery, priorityFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredData.length / PAGE_SIZE));

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredData.slice(start, start + PAGE_SIZE);
  }, [filteredData, currentPage]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const toggleFilterValue = (setFn) => (value, checked) => {
    setFn((prev) => {
      const next = new Set(prev);
      checked ? next.add(value) : next.delete(value);
      return next;
    });
    setCurrentPage(1);
  };

  const togglePriorityValue = toggleFilterValue(setPriorityFilter);
  const toggleStatusValue = toggleFilterValue(setStatusFilter);

  const handleSelectRow = (key, checked) => {
    setSelectedRows((prev) => {
      const next = new Set(prev);
      checked ? next.add(key) : next.delete(key);
      return next;
    });
  };

  const handleSelectAll = (checked) => {
    setSelectedRows(checked ? new Set(filteredData.map((row) => row.id)) : new Set());
  };

  const handleMarkViewed = () => {
    const ids = Array.from(selectedRows);
    if (onMarkViewed) {
      onMarkViewed(ids);
    } else {
      console.log('mark as viewed', ids);
    }
    setSelectedRows(new Set());
  };

  const handleDelete = () => {
    const ids = Array.from(selectedRows);
    if (onDelete) {
      onDelete(ids);
    } else {
      console.log('delete', ids);
    }
    setSelectedRows(new Set());
  };

  const activeFilterCount = priorityFilter.size + statusFilter.size;

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

        {selectedRows.size > 0 && (
          <div className="announcements__selected-actions">
            <span className="announcements__selected-count">{selectedRows.size} selected</span>
            <Button variant="outline" size="sm" onClick={handleMarkViewed}>
              <CheckCircle2 className="announcements__btn-icon" />
              Mark as viewed
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDelete}>
              <Trash2 className="announcements__btn-icon" />
              Delete
            </Button>
          </div>
        )}
      </div>

      <div className="announcements__filters">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <ListFilter className="announcements__btn-icon" />
              Priority
              {priorityFilter.size > 0 && (
                <Badge variant="secondary" className="announcements__filter-badge">
                  {priorityFilter.size}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Filter by priority</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {PRIORITY_OPTIONS.map((opt) => (
              <DropdownMenuCheckboxItem
                key={opt.value}
                checked={priorityFilter.has(opt.value)}
                onCheckedChange={(checked) => togglePriorityValue(opt.value, checked)}
                onSelect={(e) => e.preventDefault()}
              >
                {opt.label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

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
              setPriorityFilter(new Set());
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
        data={paginatedData}
        rowKey={(row) => row.id}
        loading={loading}
        selectable
        selectedRows={selectedRows}
        onSelectRow={handleSelectRow}
        onSelectAll={handleSelectAll}
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
