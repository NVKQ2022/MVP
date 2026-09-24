import StudentLayout from '@/layouts/StudentLayout';
import StudentHome from '@/pages/student/Home';
import StudentProfile from '@/pages/student/Profile';
import StudentAnnouncements from '@/pages/student/Announcements';
import AnnouncementDetail from '@/pages/student/AnnouncementDetail';
import NotFound from '@/pages/errors/NotFound';
import { StudentRoute } from './StudentRoute';
import { ProtectedRoute } from './ProtectedRoute';

export const studentRoutes = [
  {
    path: '/',
    element: (
      <StudentRoute>
        <StudentLayout />
      </StudentRoute>
    ),
    children: [
      { index: true, element: <StudentHome /> },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <StudentProfile />
          </ProtectedRoute>
        ),
      },
      {
        path: 'announcements',
        element: (
          <ProtectedRoute>
            <StudentAnnouncements />
          </ProtectedRoute>
        ),
      },
      {
        path: 'announcements/:id',
        element: (
          <ProtectedRoute>
            <AnnouncementDetail />
          </ProtectedRoute>
        ),
      },

      { path: '*', element: <NotFound /> },
    ],
  },
];
