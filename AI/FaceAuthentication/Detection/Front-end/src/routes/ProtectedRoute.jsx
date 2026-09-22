import { Navigate } from 'react-router-dom';
import { useLogin } from '@/features/auth/hooks/useLogin';

export function ProtectedRoute({ children }) {
  const { isAuthenticated } = useLogin();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
