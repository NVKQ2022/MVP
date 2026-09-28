import { useAuth } from '@/features/auth/hooks/useAuth';
import { env } from '@/config/env';

export function AdminRoute({ children }) {
  const { user, status } = useAuth();

  // if (status === 'idle' || status === 'loading') {
  //   return <div className="p-8 text-sm text-muted-foreground">Loading…</div>;
  // }

  if (!user || user.role !== 'Admin') {
    const port = window.location.port ? `:${window.location.port}` : '';
    window.location.assign(`http://${env.adminHost}${port}/login`);
    return null;
  }

  return children;
}
