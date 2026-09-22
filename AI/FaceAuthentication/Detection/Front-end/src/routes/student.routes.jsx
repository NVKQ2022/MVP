import StudentLayout from '@/layouts/StudentLayout';
import StudentHome from '@/pages/student/Home';
import StudentProfile from '@/pages/student/Profile';
import StudentAnnouncements from '@/pages/student/Announcements';
import AnnouncementDetail from '@/pages/student/AnnouncementDetail';
import NotFound from '@/pages/errors/NotFound';
import { StudentRoute } from './StudentRoute';

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
      { path: 'profile', element: <StudentProfile /> },
      { path: 'announcements', element: <StudentAnnouncements /> },
      { path: 'announcements/:id', element: <AnnouncementDetail /> },

      { path: '*', element: <NotFound /> },
    ],
  },
];
