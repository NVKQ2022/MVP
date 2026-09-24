import AdminLayout from '@/layouts/AdminLayout';
import AdminDashboard from '@/pages/admin/Dashboard';
import AdminUsers from '@/pages/admin/Users';
import AdminUserDetail from '@/pages/admin/UserDetail';
import AdminWhitelist from '@/pages/admin/Whitelist';
import AdminAnnouncements from '@/pages/admin/Announcements';
import { AdminAnnouncementDetail, AdminAnnouncementWriteDetail } from '@/pages/admin/AnnouncementDetail';
import AdminAuditLogs from '@/pages/admin/AuditLogs';
import NotFound from '@/pages/errors/NotFound';
import AuthCallback from '@/pages/auth/Callback';
import { AdminRoute } from './AdminRoute';

export const adminRoutes = [
  {
    // Must sit OUTSIDE AdminRoute — the session doesn't exist on this
    // origin yet when this route is hit.
    path: '/auth/callback',
    element: <AuthCallback />,
  },
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
      { path: 'announcements/create', element: <AdminAnnouncementWriteDetail /> },
      { path: 'announcements/edit/:id', element: <AdminAnnouncementWriteDetail /> },
      { path: 'announcements/:id', element: <AdminAnnouncementDetail /> },
      { path: 'audit-logs', element: <AdminAuditLogs /> },

      { path: '*', element: <NotFound /> },
    ],
  },
];
