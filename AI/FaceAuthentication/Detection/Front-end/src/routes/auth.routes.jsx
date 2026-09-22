import AuthLayout from '@/layouts/AuthLayout';
import Login from '@/pages/auth/Login';

// Mounted alongside student routes — login lives on the root domain.
export const authRoutes = [
  {
    path: '/login',
    element: <AuthLayout />,
    children: [{ index: true, element: <Login /> }],
  },
];
