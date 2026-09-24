import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';

export function ProtectedRoute({ children }) {
  const { status, isAuthenticated } = useAuth();
  const location = useLocation();

  // if (status === 'idle' || status === 'loading') {
  //   return <div className="p-8 text-sm text-muted-foreground">Loading…</div>;
  // }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
