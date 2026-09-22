import { useCallback, useSyncExternalStore } from 'react';
import { loginRequest } from '@/features/auth/services/auth.api';
import { authStore } from '@/features/auth/auth.store';

export function useLogin() {
  const { user } = useSyncExternalStore(authStore.subscribe, authStore.getSnapshot);

  const login = async ({ email, password }) => {
    const result = await loginRequest({
      email,
      password,
    });

    if (!result.success) {
      throw new Error(result.message || 'Unable to sign in.');
    }

    authStore.setUser(result.user);

    return result.user;
  };

  const logout = useCallback(() => {
    authStore.clear();
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    login,
    logout,
  };
}
