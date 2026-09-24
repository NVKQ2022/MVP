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
  const navigate = useNavigate();
  const totalUsers = mockUsers.length;
  const activeUsers = mockUsers.filter((user) => user.status === 'active').length;
  const otherStateUsers = mockUsers.filter((user) => user.status !== 'inactive').length;
  const admins = mockUsers.filter((user) => user.role === 'Admin');
  return (
    <div className="dashboard_style">

      {/* Statistics */}
      <div className="admin_dashboard_stats">
        <Card
          className="admin_dashboard_stats_element"
          onClick={() => navigate('/users')}
        >
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="admin_dashboard_stats_element_content">
              {totalUsers}
            </p>
          </CardContent>
        </Card>
        <Card
          className="admin_dashboard_stats_element"
          onClick={() => navigate('/users?status=active')}
        >
          <CardHeader>
            <CardTitle>Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="admin_dashboard_stats_element_content">
              {activeUsers}
            </p>
          </CardContent>
        </Card>
        <Card
          className="admin_dashboard_stats_element"
          onClick={() => navigate('/users?status=non-active')}
        >
          <CardHeader>
            <CardTitle>Users of other states</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="admin_dashboard_stats_element_content">
              {otherStateUsers}
            </p>
          </CardContent>
        </Card>

      </div>

      {/* Recent users */}
      <Card>

        <CardHeader className="admin_dashboard_admin_list_title">
          <CardTitle>Administrators</CardTitle>
        </CardHeader>
        <CardContent>
          {admins.length === 0 ? (
            <div className="admin_dashboard_admin_list_empty_indicate">
              No users registered
            </div>
          ) : (
            <div className="admin_dashboard_admin_list_nonempty">
              {admins.map((user) => (
                <div
                  key={user.id}
                  className="admin_dashboard_admin_list_element"
                  onClick={() => navigate(`/users/${user.id}`)}
                >
                  <div>
                    <p className="admin_dashboard_admin_name">
                      {user.name}
                    </p>
                    <p className="admin_dashboard_admin_email">
                      {user.email}
                    </p>
                  </div>
                  <div className="admin_dashboard_admin_right_info">
                    <Badge
                      variant={
                        user.status === 'active'
                          ? 'default'
                          : 'secondary'
                      }
                    >
                      {user.status}
                    </Badge>
                    <p className="admin_dashboard_admin_created_at">
                      {user.createdAt}
                    </p>
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