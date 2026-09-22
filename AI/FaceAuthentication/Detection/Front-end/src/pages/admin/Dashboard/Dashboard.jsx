import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';
import { Badge } from '@/components/ui/badge/badge';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { mockUsers } from '@/features/users/mock-data';

export default function AdminDashboard() {
  // const [displayedAdmins, setDisplayedAdmins] = useState(3);
  const navigate = useNavigate();

  const totalUsers = mockUsers.length;

  const activeUsers = mockUsers.filter((user) => user.status === 'active').length;

  const otherStateUsers = mockUsers.filter((user) => user.status !== 'inactive').length;

  const admins = mockUsers.filter((user) => user.role === 'Admin');

  // .slice(0, displayedAdmins)
  return (
    <div className="space-y-6 p-8">
      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="cursor-pointer hover:bg-muted" onClick={() => navigate('/users')}>
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-3xl font-bold">{totalUsers}</p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:bg-muted"
          onClick={() => navigate('/users?status=active')}
        >
          <CardHeader>
            <CardTitle>Active Users</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-3xl font-bold">{activeUsers}</p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:bg-muted"
          onClick={() => navigate('/users?status=non-active')}
        >
          <CardHeader>
            <CardTitle>Users of other states</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-3xl font-bold">{otherStateUsers}</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent users */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Administrators</CardTitle>
        </CardHeader>

        <CardContent>
          {admins.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              No users registered
            </div>
          ) : (
            <div className="space-y-2">
              {admins.map((user) => (
                <div
                  key={user.id}
                  className="flex cursor-pointer items-center justify-between rounded-md p-3 hover:bg-muted"
                  onClick={() => navigate(`/users/${user.id}`)}
                >
                  <div>
                    <p className="font-medium">{user.name}</p>

                    <p className="text-sm text-muted-foreground">{user.email}</p>
                  </div>

                  <div className="flex items-center gap-4">
                    <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                      {user.status}
                    </Badge>

                    <p className="text-sm text-muted-foreground">{user.createdAt}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
