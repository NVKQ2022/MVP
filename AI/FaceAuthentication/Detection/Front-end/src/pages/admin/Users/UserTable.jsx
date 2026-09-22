import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table/table';
import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

// uesr model
// {
// id: 'u1',
// name: 'Nguyen Van A',
// email: 'nguyenvana@eduportal.vn',
// password: 'eduportal',
// role: 'Student',
// status: 'active',
// createdAt: '2026-01-12',
// }

export default function UserTable({ users }) {
  const navigate = useNavigate();
  const [sortConfig, setSortConfig] = useState({
    key: null,
    direction: 'asc',
  });
  const handleSort = (key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };
  const sortedUsers = [...users].sort((a, b) => {
    if (!sortConfig.key) return 0;

    const valueA = a[sortConfig.key];
    const valueB = b[sortConfig.key];

    if (valueA < valueB) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }

    if (valueA > valueB) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }

    return 0;
  });
  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return '↕';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="cursor-pointer" onClick={() => handleSort('id')}>
            ID {getSortIcon('id')}
          </TableHead>

          <TableHead className="cursor-pointer" onClick={() => handleSort('name')}>
            Name {getSortIcon('name')}
          </TableHead>

          <TableHead className="cursor-pointer" onClick={() => handleSort('email')}>
            Email {getSortIcon('email')}
          </TableHead>

          <TableHead className="cursor-pointer" onClick={() => handleSort('role')}>
            Role {getSortIcon('role')}
          </TableHead>

          <TableHead className="cursor-pointer" onClick={() => handleSort('status')}>
            Status {getSortIcon('status')}
          </TableHead>

          <TableHead className="text-right">Action</TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {sortedUsers.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="h-24 text-center">
              No users registered
            </TableCell>
          </TableRow>
        ) : (
          sortedUsers.map((user) => (
            <TableRow
              key={user.id}
              className="cursor-pointer hover:bg-muted"
              onClick={() => navigate(`/users/${user.id}`)}
            >
              <TableCell>{user.id}</TableCell>
              <TableCell className="font-medium">{user.name}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.role}</TableCell>
              <TableCell>
                <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                  {user.status}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <Button
                  variant={user.status === 'active' ? 'destructive' : 'secondary'}
                  onClick={(e) => {
                    e.stopPropagation();
                    // activate/deactivate logic
                  }}
                >
                  {user.status === 'active' ? 'Deactivate' : 'Activate'}
                </Button>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
}
