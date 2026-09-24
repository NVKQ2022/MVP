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
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { Archive, ListFilter, MoreVertical, Pencil, Plus, Search, Send, Trash2 } from 'lucide-react';
import { toast } from '@/components/common/Toaster/toast';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { ErrorState } from '@/components/common/ErrorState';
import {
  useAnnouncementsQuery,
  useArchiveAnnouncement,
  useDeleteAnnouncement,
  usePublishAnnouncement,
} from '@/features/AdminAnnouncement';

const PAGE_SIZE = 10;

const STATUS_LABEL = {
  Published: { label: 'Published', variant: 'default' },
  Draft: { label: 'Draft', variant: 'outline' },
  Archived: { label: 'Archived', variant: 'secondary' },
};

const STATUS_OPTIONS = [
  { value: 'Published', label: 'Published' },
  { value: 'Draft', label: 'Draft' },
  { value: 'Archived', label: 'Archived' },
];

const buildColumns = (onOpenDetail) => [
  {
    key: 'title',
    header: 'Title',
    render: (row) => (
      <span
        className="admin-announcements__row-title admin-announcements__row-title--clickable"
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
    key: 'publicationStatus',
    header: 'Status',
    render: (row) => {
      const s = STATUS_LABEL[row.publicationStatus] ?? { label: row.publicationStatus, variant: 'default' };
      return <Badge variant={s.variant}>{s.label}</Badge>;
    },
  },
];

const AdminAnnouncements = () => {
  const navigate = useNavigate();
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(new Set());

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useAnnouncementsQuery({
    pageNumber: currentPage,
    pageSize: PAGE_SIZE,
    search: searchQuery.trim() || undefined,
    status: statusFilter.size > 0 ? Array.from(statusFilter) : undefined,
  });

  const deleteMutation = useDeleteAnnouncement();
  const publishMutation = usePublishAnnouncement();
  const archiveMutation = useArchiveAnnouncement();

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

  const handleSelectRow = (key, checked) => {
    setSelectedRows((prev) => {
      const next = new Set(prev);
      checked ? next.add(key) : next.delete(key);
      return next;
    });
  };

  const handleSelectAll = (checked) => {
    setSelectedRows(checked ? new Set(items.map((row) => row.id)) : new Set());
  };

  const handleDeleteClick = () => {
    setConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    const ids = Array.from(selectedRows);

    const results = await Promise.allSettled(
      ids.map((id) => deleteMutation.mutateAsync(id))
    );

    const failed = [];
    const succeededIds = [];

    results.forEach((result, index) => {
      const id = ids[index];
      if (result.status === 'fulfilled') {
        succeededIds.push(id);
      } else {
        const row = items.find((item) => item.id === id);
        failed.push({ id, title: row?.title ?? id, error: result.reason });
      }
    });

    setSelectedRows(new Set(failed.map((item) => item.id)));

    if (failed.length > 0) {
      failed.forEach((item) => console.error(`Failed to delete announcement ${item.id}:`, item.error));
    }

    if (succeededIds.length > 0 && failed.length === 0) {
      toast.success(`Deleted ${succeededIds.length} announcement${succeededIds.length > 1 ? 's' : ''}`);
    } else if (failed.length > 0) {
      const prefix =
        succeededIds.length > 0
          ? `Deleted ${succeededIds.length}, failed to delete ${failed.length}`
          : 'Failed to delete announcements';
      toast.error(prefix, {
        description: `Could not delete: ${failed.map((item) => item.title).join(', ')}`,
      });
    }
  };

  const handleCreate = () => {
    navigate('/announcements/create');
  };

  const handleUpdate = (row) => {
    navigate(`/announcements/edit/${row.id}`);
  };

  const handleOpenDetail = (row) => {
    navigate(`/announcements/${row.id}`);
  };

  const handlePublish = async (row) => {
    if (!canPublish(row)) return;
    try {
      await publishMutation.mutateAsync(row.id);
      toast.success(`Published "${row.title}"`);
    } catch (error) {
      console.error(`Failed to publish announcement ${row.id}:`, error);
      toast.error('Failed to publish announcement', {
        description: error?.message ?? 'Please try again.',
      });
    }
  };

  const handleArchive = async (row) => {
    if (!canArchive(row)) return;
    try {
      await archiveMutation.mutateAsync(row.id);
      toast.success(`Archived "${row.title}"`);
    } catch (error) {
      console.error(`Failed to archive announcement ${row.id}:`, error);
      toast.error('Failed to archive announcement', {
        description: error?.message ?? 'Please try again.',
      });
    }
  };

  const canPublish = (row) => row.publicationStatus === 'DRAFT';
  console.log(canPublish);
  const canArchive = (row) => row.publicationStatus === 'PUBLISHED';

  const columns = buildColumns(handleOpenDetail);

  const actions = (row) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Open actions for announcement ${row.title}`}
        >
          <MoreVertical className="admin-announcements__row-action-icon" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onSelect={() => handleUpdate(row)}>
          <Pencil className="admin-announcements__row-menu-icon" />
          Update
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={!canPublish(row)}
          onSelect={() => handlePublish(row)}
        >
          <Send className="admin-announcements__row-menu-icon" />
          Publish
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={!canArchive(row)}
          onSelect={() => handleArchive(row)}
        >
          <Archive className="admin-announcements__row-menu-icon" />
          Archive
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );

  const activeFilterCount = statusFilter.size;

  if (isError) {
    return (
      <div className="admin-announcements">
        <h2 className="admin-announcements__title">Admin Announcements</h2>
        <ErrorState
          title="Failed to load announcements"
          description="We couldn't load the announcements list. Please try again."
          onRetry={refetch}
        />
      </div>
    );
  }

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