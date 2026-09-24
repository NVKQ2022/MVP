import { useCallback, useSyncExternalStore } from 'react';
import { authApi } from '../services/auth.api';
import { authStore } from '../auth.store';
import { decodeAccessToken } from '../utils/jwtDecode';

export function useAuth() {
  const { user, status } = useSyncExternalStore(authStore.subscribe, authStore.getSnapshot);

  const login = useCallback(async ({ email, password }) => {
    const session = await authApi.login({ email, password });
    const user = decodeAccessToken(session?.accessToken);
    authStore.setSession({
      user,
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    });
    return {
      user,
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    };
  }, []);

  const faceLogin = useCallback(async (formData) => {
    const session = await authApi.faceLogin(formData);
    const user = decodeAccessToken(session?.accessToken);
    authStore.setSession({
      user,
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    });
    return {
      user,
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
    };
  }, []);

  const register = useCallback(async ({ name, email, password }) => {
    return authApi.register({ name, email, password });
  }, []);

  const verifyEmail = useCallback(async ({ email, otp }) => {
    return authApi.verifyEmail({ email, otp });
  }, []);

  const logout = useCallback(async () => {
    const { refreshToken } = authStore.getSnapshot();
    try {
      if (refreshToken) {
        authStore.clear();
        await authApi.logout(refreshToken);
      }
    } catch {
      // Best-effort - clear the local session regardless of API result.
    } finally {
      authStore.clear();
    }
  }, []);

  return {
    user,
    status, // 'idle' | 'loading' | 'authenticated' | 'unauthenticated'
    isAuthenticated: status === 'authenticated',
    login,
    faceLogin,
    register,
    verifyEmail,
    logout,
  };
}
