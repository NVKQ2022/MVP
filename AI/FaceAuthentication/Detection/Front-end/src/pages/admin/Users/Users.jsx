import { Card, CardContent } from '@/components/ui/card/card';
import { Button } from '@/components/ui/button/button';
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/input/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import { Badge } from '@/components/ui/badge/badge';
import { useAdminUsersQuery, useAdminUserQuery, useAdminUserDelete, useAdminUserUpdate } from '@/features/AdminUsers';
import { DataTable } from '@/components/common/DataTable';
import { AppPagination } from '@/components/common/AppPagination';
import { PageHeader } from '@/components/common/PageHeader';

const PAGE_SIZE = 5;

const IS_ACTIVE = {
  ALL: "all",
  TRUE: "true",
  FALSE: "false"
}

const columns = [
  {
    key: 'userName',
    header: 'User name',
    render: (row) => <span>{row.userName}</span>,
  },
  {
    key: 'email',
    header: 'Email',
    render: (row) => <span>{row.email}</span>,
  },
  {
    key: 'role',
    header: 'Role',
    render: (row) => <span>{row.roleName}</span>
  },
  {
    key: 'isActive',
    header: 'Active state',
    render: (row) => (
      <Badge variant={row.isActive ? 'default' : 'secondary'}>
        {row.isActive ? 'Active' : 'Inactive'}
      </Badge>
    ),
  }
];

function removeToneMarker(text) {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D');
}

export default function AdminUsers() {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPerPage, setUsersPerPage] = useState(5);
  const [searchParams] = useSearchParams();
  const [isActiveFilter, setIsActiveFilter] = useState(() => {
    const isActive = searchParams.get('isActive');
    if (isActive === 'true') return IS_ACTIVE.TRUE;
    if (isActive === 'false') return IS_ACTIVE.FALSE;
    return IS_ACTIVE.ALL;
  });
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('active');
  const [pageSize, setPageSize] = useState(PAGE_SIZE);
  const { data, isLoading } = useAdminUsersQuery({
    page: currentPage,
    pageSize: pageSize,
    search: searchQuery.trim() || undefined,
    isActive: isActiveFilter === IS_ACTIVE.ALL ? undefined : isActiveFilter === IS_ACTIVE.TRUE
  });

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, isActiveFilter, pageSize]);

  const items = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;
  console.log('items: ', items);

  const handleSelectRow = (key, checked) => {
    setSelectedRows((prev) => {
      const next = new Set(prev);
      checked ? next.add(key) : next.delete(key);
      return next;
    });
  };

  return (
    <div className="admin_users_wrapper">
      <PageHeader
        title="User account list"
        description="Manage student accounts and other admin accounts"
      />
      <Card>
        <CardContent className="admin_user_list_wrapper">
          <div className='filter_wrapper'>
            <Input
              type="text"
              placeholder="Search by name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Select value={isActiveFilter} onValueChange={setIsActiveFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={IS_ACTIVE.ALL}>All</SelectItem>
                <SelectItem value={IS_ACTIVE.TRUE}>Active</SelectItem>
                <SelectItem value={IS_ACTIVE.FALSE}>Not active</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Select
            value={String(pageSize)}
            onValueChange={(val) => setPageSize(Number(val))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5">5 users maximum</SelectItem>
              <SelectItem value="10">10 users maximum</SelectItem>
            </SelectContent>
          </Select>
          <DataTable
            columns={columns}
            data={items}
            rowKey={(row) => row.id}
            loading={isLoading}
            selectedRows={selectedRows}
            onSelectRow={handleSelectRow}
            emptyMessage="No users found"
            actions={(row) => (
              <Button size="sm" variant="outline" onClick={() => navigate(`/users/${row.id}`)}>
                Detail
              </Button>
            )}
          />
          <AppPagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </CardContent>
      </Card>
    </div >
  );
}