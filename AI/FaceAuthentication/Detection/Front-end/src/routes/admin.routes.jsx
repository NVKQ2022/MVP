import AdminLayout from '@/layouts/AdminLayout';
import AdminDashboard from '@/pages/admin/Dashboard';
import AdminUsers from '@/pages/admin/Users';
import AdminUserDetail from '@/pages/admin/UserDetail';
import AdminWhitelist from '@/pages/admin/Whitelist';
import AdminAnnouncements from '@/pages/admin/Announcements';
import AdminAnnouncementDetail from '@/pages/admin/AnnouncementDetail';
import AdminAuditLogs from '@/pages/admin/AuditLogs';
import NotFound from '@/pages/errors/NotFound';
import { AdminRoute } from './AdminRoute';

export const adminRoutes = [
  {
    path: '/',
    element: (
      <AdminRoute>
        <AdminLayout />
      </AdminRoute>
    ),
    children: [
      { index: true, element: <AdminDashboard /> },
      { path: 'users', element: <AdminUsers /> },
      { path: 'users/:id', element: <AdminUserDetail /> },
      { path: 'whitelist', element: <AdminWhitelist /> },
      { path: 'announcements', element: <AdminAnnouncements /> },
      { path: 'announcements/create', element: <AdminAnnouncementDetail /> },
      { path: 'announcements/:id', element: <AdminAnnouncementDetail /> },
      { path: 'audit-logs', element: <AdminAuditLogs /> },

      { path: '*', element: <NotFound /> },
    ],
  },
];
