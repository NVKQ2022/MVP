import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';
import { Badge } from '@/components/ui/badge/badge';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminUsersQuery } from '@/features/AdminUsers';
import { formatDate } from '@/utils/formatDate';
import { PageHeader } from '@/components/common/PageHeader';

const PAGE_SIZE = 5;
const ROLE = {
  ADMIN: '11111111-1111-1111-1111-111111111111',
  STUDENT: '22222222-2222-2222-2222-222222222222',
};

export default function AdminDashboard() {
  const navigate = useNavigate();

  // separate queries — one for stats (all users), one for admin list
  const { data: allData } = useAdminUsersQuery({
    page: 1,
    pageSize: 1, // just need totalCount, not the items
  });

  const [adminPage, setAdminPage] = useState(1);
  const { data: adminData, isLoading: adminLoading } = useAdminUsersQuery({
    page: adminPage,
    pageSize: PAGE_SIZE,
    roleId: ROLE.ADMIN,
  });

  const { data: activeData } = useAdminUsersQuery({
    page: 1,
    pageSize: 1,
    isActive: true,
  });

  const { data: inactiveData } = useAdminUsersQuery({
    page: 1,
    pageSize: 1,
    isActive: false,
  });

  const totalUsers = allData?.totalCount ?? 0;
  const activeUsers = activeData?.totalCount ?? 0;
  const inactiveUsers = inactiveData?.totalCount ?? 0;
  const adminItems = adminData?.items ?? [];

  return (
    <div className="dashboard_style">
      <PageHeader
        title="Dashboard"
        description="Quick glance at the system status"
      />
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
          onClick={() => navigate('/users?isActive=true')}
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
          onClick={() => navigate('/users?isActive=false')}
        >
          <CardHeader>
            <CardTitle>Inactive Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="admin_dashboard_stats_element_content">
              {inactiveUsers}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Administrators list */}
      <Card>
        <CardHeader className="admin_dashboard_admin_list_title">
          <CardTitle>Administrators</CardTitle>
        </CardHeader>
        <CardContent>
          {adminLoading ? (
            <div>Loading...</div>
          ) : adminItems.length === 0 ? (
            <div className="admin_dashboard_admin_list_empty_indicate">
              No administrators found
            </div>
          ) : (
            <div className="admin_dashboard_admin_list_nonempty">
              {adminItems.map((user) => (
                <div
                  key={user.id}
                  className="admin_dashboard_admin_list_element"
                  onClick={() => navigate(`/users/${user.id}`)}
                >
                  <div>
                    <p className="admin_dashboard_admin_name">
                      {user.userName}
                    </p>
                    <p className="admin_dashboard_admin_email">
                      {user.email}
                    </p>
                  </div>
                  <div className="admin_dashboard_admin_right_info">
                    <Badge variant={user.isActive ? 'default' : 'secondary'}>
                      {user.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                    <p className="admin_dashboard_admin_created_at">
                      {formatDate(user.createdAt)}
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