import { DataTable } from '@/components/common/DataTable';
import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog/dialog';
import { Input } from '@/components/ui/input/input';
import { Label } from '@/components/ui/label/label';
import {
  useWhitelistQuery,
  useCreateWhitelist,
  useUpdateWhitelist,
  useActivateWhitelist,
  useDeactivateWhitelist,
  useDeleteWhitelist,
} from '@/features/AdminWhitelist';
import { useState } from 'react';
import { MoreVertical, Pencil, ToggleLeft, ToggleRight, Trash2, Plus } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { AppPagination } from '@/components/common/AppPagination';

const columns = [
  {
    key: 'type',
    header: 'Item type',
    render: (row) => <span>{row.email !== null ? 'Email' : 'Domain name'}</span>,
  },
  {
    key: 'value',
    header: 'Value',
    render: (row) => <span>{row.email !== null ? row.email : row.domain}</span>,
  },
  {
    key: 'isActive',
    header: '',
    render: (row) => (
      <Badge variant={row.isActive ? 'default' : 'secondary'}>
        {row.isActive ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
  {
    key: 'updatedAt',
    header: 'Updated at',
    render: (row) => <span>{row.updatedAt}</span>,
  },
  {
    key: 'createdBy',
    header: 'Created by',
    render: (row) => <span>{row.createdBy}</span>,
  },
];

const PAGE_SIZE = 5;

const EMPTY_FORM = { email: '', domain: '' };

export default function AdminWhitelist() {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE);

  // modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRow, setEditingRow] = useState(null); // null = create, object = update
  const [form, setForm] = useState(EMPTY_FORM);

  const emailFilled = form.email.trim() !== '';
  const domainFilled = form.domain.trim() !== '';

  const { data, isLoading } = useWhitelistQuery({ page: currentPage, pageSize });
  const items = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;

  const createWhitelist = useCreateWhitelist();
  const updateWhitelist = useUpdateWhitelist();
  const activateWhitelist = useActivateWhitelist();
  const deactivateWhitelist = useDeactivateWhitelist();
  const deleteWhitelist = useDeleteWhitelist();

  const handleFormChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  // open modal for create
  const handleOpenCreate = () => {
    setEditingRow(null);
    setForm(EMPTY_FORM);
    setModalOpen(true);
  };

  // open modal for edit
  const handleEdit = (row) => {
    setEditingRow(row);
    setForm({ email: row.email ?? '', domain: row.domain ?? '' });
    setModalOpen(true);
  };

  const handleSubmit = () => {
    if (editingRow) {
      updateWhitelist.mutate({
        id: editingRow.id,
        email: form.email || null,
        domain: form.domain || null,
      }, {
        onSuccess: () => setModalOpen(false),
        onError: () => alert('Failed to update whitelist item'),
      });
    } else {
      createWhitelist.mutate({
        email: form.email || null,
        domain: form.domain || null,
      }, {
        onSuccess: () => setModalOpen(false),
        onError: () => alert('Failed to create whitelist item'),
      });
    }
  };

  const handleToggleActive = (row) => {
    if (row.isActive) {
      deactivateWhitelist.mutate(row.id, {
        onError: () => alert('Failed to deactivate'),
      });
    } else {
      activateWhitelist.mutate(row.id, {
        onError: () => alert('Failed to activate'),
      });
    }
  };

  const handleDelete = (row) => {
    deleteWhitelist.mutate(row.id, {
      onError: () => alert('Failed to delete whitelist item'),
    });
  };

  const isPending =
    createWhitelist.isPending ||
    updateWhitelist.isPending;

  const actions = (row) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Open actions">
          <MoreVertical size={16} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onSelect={() => handleEdit(row)}>
          <Pencil size={14} />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={() => handleToggleActive(row)}>
          {row.isActive ? <ToggleLeft size={14} /> : <ToggleRight size={14} />}
          {row.isActive ? 'Deactivate' : 'Activate'}
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={() => handleDelete(row)}>
          <Trash2 size={14} />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );

  return (
    <>
      <PageHeader
        title="Email & Domain Whitelist"
        description="Manage allowed email addresses and domains"
        actions={
          <Button onClick={handleOpenCreate}>
            <Plus size={16} />
            Add Item
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={items}
        rowKey={(row) => row.id}
        loading={isLoading}
        emptyMessage="No whitelist item found"
        actions={actions}
      />

      <AppPagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingRow ? 'Edit Whitelist Item' : 'Add Whitelist Item'}</DialogTitle>
            <DialogDescription>
              {editingRow
                ? 'Update the email or domain for this whitelist entry.'
                : 'Enter an email address or a domain name to whitelist.'}
            </DialogDescription>
          </DialogHeader>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                placeholder="user@example.com"
                value={form.email}
                onChange={handleFormChange('email')}
                disabled={domainFilled}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              <Label htmlFor="domain">Domain</Label>
              <Input
                id="domain"
                placeholder="example.com"
                value={form.domain}
                onChange={handleFormChange('domain')}
                disabled={emailFilled}
              />
            </div>
          </div>

          <DialogDescription>
            Enter either an email address or a domain name — not both.
          </DialogDescription>

          <DialogFooter>
            <Button
              variant="outline"
              disabled={isPending}
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button disabled={isPending} onClick={handleSubmit}>
              {isPending ? 'Saving...' : editingRow ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}