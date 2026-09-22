import { Navigate } from 'react-router-dom';
import { useLogin } from '@/features/auth/hooks/useLogin';

export function StudentRoute({ children }) {
  const { user } = useLogin();

  if (user?.role === 'admin') {
    return <Navigate to="/login" replace />;
  }

  return children;
}
