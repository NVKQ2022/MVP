import { useMemo, useState } from 'react';
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
import { ListFilter, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { announcementsData } from '@/data/announcementsData';
import StudentAnnouncements from '@/pages/student/Announcements';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';

const PAGE_SIZE = 5;

const PRIORITY_LABEL = {
  high: { label: 'High', variant: 'destructive' },
  medium: { label: 'Medium', variant: 'default' },
  low: { label: 'Low', variant: 'secondary' },
};

const STATUS_LABEL = {
  published: { label: 'Published', variant: 'default' },
  draft: { label: 'Draft', variant: 'outline' },
  archived: { label: 'Archived', variant: 'secondary' },
};

// Filter option lists
const PRIORITY_OPTIONS = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const STATUS_OPTIONS = [
  { value: 'published', label: 'Published' },
  { value: 'draft', label: 'Draft' },
  { value: 'archived', label: 'Archived' },
];

const columns = [
  {
    key: 'title',
    header: 'Title',
    render: (row) => <span className="admin-announcements__row-title">{row.title}</span>,
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
      const s = STATUS_LABEL[row.status] ?? { label: row.status, variant: 'default' };
      return <Badge variant={s.variant}>{s.label}</Badge>;
    },
  },
];

const AdminAnnouncements = ({
  data = announcementsData,
  loading = false,
  onDelete, // (ids: string[]) => void — called with the selected row ids
}) => {
  const navigate = useNavigate();
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmOpen, setConfirmOpen] = useState(false);
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

      const matchesStatus = statusFilter.size === 0 || statusFilter.has(row.status);

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

  const handleDeleteClick = () => {
    setConfirmOpen(true);
  };

  const handleConfirmDelete = () => {
    const ids = Array.from(selectedRows);

    // TODO: Call API delete announcement here.
    if (onDelete) {
      onDelete(ids);
    } else {
      console.log('delete', ids);
    }

    setSelectedRows(new Set());
  };

  const handleCreate = () => {
    navigate('/announcements/create');
  };

  const handleUpdate = (row) => {
    navigate(`/announcements/${row.id}`, { state: { announcement: row } });
  };

  const actions = useMemo(
    () => (row) => (
      <Button
        variant="ghost"
        size="icon"
        onClick={() => handleUpdate(row)}
        aria-label={`Update announcement ${row.title}`}
      >
        <Pencil className="admin-announcements__row-action-icon" />
      </Button>
    ),
    [],
  );

  const activeFilterCount = priorityFilter.size + statusFilter.size;

  return (
    <div className="admin-announcements">
      <h2 className="admin-announcements__title">Admin Announcements</h2>

      <div className="admin-announcements__toolbar">
        <div className="admin-announcements__search">
          <Search className="admin-announcements__search-icon" />
          <Input
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search announcements..."
            className="admin-announcements__search-input"
          />
        </div>

        <div className="admin-announcements__actions">
          {selectedRows.size > 0 && (
            <>
              <span className="admin-announcements__selected-count">
                {selectedRows.size} selected
              </span>
              <Button variant="destructive" size="sm" onClick={handleDeleteClick}>
                <Trash2 className="admin-announcements__btn-icon" />
                Delete
              </Button>
            </>
          )}
          <Button size="sm" onClick={handleCreate}>
            <Plus className="admin-announcements__btn-icon" />
            Create
          </Button>
        </div>
      </div>

      <div className="admin-announcements__filters">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <ListFilter className="admin-announcements__btn-icon" />
              Priority
              {priorityFilter.size > 0 && (
                <Badge variant="secondary" className="admin-announcements__filter-badge">
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
              <ListFilter className="admin-announcements__btn-icon" />
              Status
              {statusFilter.size > 0 && (
                <Badge variant="secondary" className="admin-announcements__filter-badge">
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
        actions={actions}
        emptyMessage="No announcements found"
      />

      <AppPagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Delete Annoucement?"
        description={`Are you sure you want to delete ${selectedRows.size} selected annoucements? This action cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="destructive"
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
};

export default AdminAnnouncements;
