import AuthLayout from '@/layouts/AuthLayout';
import Login from '@/pages/auth/Login';
import Signup from '@/pages/auth/Signup';
import VerifyEmail from '@/pages/auth/VerifyEmail';

export const authRoutes = [
  {
    path: '/login',
    element: <AuthLayout />,
    children: [{ index: true, element: <Login /> }],
  },
  {
    path: '/signup',
    element: <AuthLayout />,
    children: [{ index: true, element: <Signup /> }],
  },
  {
    path: '/verify-email',
    element: <AuthLayout />,
    children: [{ index: true, element: <VerifyEmail /> }],
  },
];
