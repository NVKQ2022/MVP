import { useEffect } from 'react';
import { authStore } from '../../auth.store';

export function AuthInitializer({ children }) {
  useEffect(() => {
    const { accessToken, status } = authStore.getSnapshot();
    if (status !== 'idle') return;

    if (!accessToken) {
      authStore.setStatus('unauthenticated');
      return;
    }
  }, []);

  return children;
}
