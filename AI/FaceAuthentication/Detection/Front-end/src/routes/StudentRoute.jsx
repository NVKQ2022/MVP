import { Navigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';

export function StudentRoute({ children }) {
  const { user, status } = useAuth();

  // if (status === 'idle' || status === 'loading') {
  //   return null;
  // }

  if (user?.role === 'Admin') {
    return <Navigate to="/login" replace />;
  }

  return children;
}
