import { Card, CardContent } from '@/components/ui/card/card';
import { Button } from '@/components/ui/button/button';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Input } from '@/components/ui/input/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import UserFilters from './UserFilters';
import UserTable from './UserTable';
import Pagination from './Pagination';
import { mockUsers } from '@/features/users/mock-data';
import { Badge } from '@/components/ui/badge/badge';

function removeToneMarker(text) {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D');
}

export default function AdminUsers() {
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPerPage, setUsersPerPage] = useState(5);
  const [searchParams] = useSearchParams();
  const initialStatus = searchParams.get('status') || 'All';
  const [statusFilter, setStatusFilter] = useState(initialStatus);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter]);

  const filteredUsers = mockUsers.filter((user) => {
    const query = removeToneMarker(search).toLowerCase();
    const matchesSearch =
      removeToneMarker(user.name)
        .toLowerCase()
        .includes(query) ||
      removeToneMarker(user.email)
        .toLowerCase()
        .includes(query);
    const matchesStatus =
      statusFilter === 'All' ||
      (statusFilter === 'non-active'
        ? user.status !== 'active'
        : user.status === statusFilter);
    return matchesSearch && matchesStatus;
  });

  const totalPages = Math.ceil(filteredUsers.length / usersPerPage);
  const startIndex = (currentPage - 1) * usersPerPage;
  const currentUsers = filteredUsers.slice(
    startIndex,
    startIndex + usersPerPage
  );

  return (
    <div className="admin_users_wrapper">
      <Card>
        <CardContent className="admin_user_list_wrapper">
          <UserFilters
            search={search}
            setSearch={setSearch}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
          />
          <UserTable users={currentUsers} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            usersPerPage={usersPerPage}
            setCurrentPage={setCurrentPage}
            setUsersPerPage={setUsersPerPage}
          />
        </CardContent>
      </Card>
    </div >
  );
}
