import { useLogin } from '@/features/auth/hooks/useLogin';
import { env } from '@/config/env';

export function AdminRoute({ children }) {
  const { user } = useLogin();

  if (!user || user.role !== 'admin') {
    const port = window.location.port ? `:${window.location.port}` : '';
    window.location.assign(`http://${env.adminHost}${port}/login`);
    return null;
  }

  return children;
}
