import { appConfig } from '@/config/appConfig';

function readStoredUser() {
  try {
    const raw = localStorage.getItem(appConfig.authStorageKey);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

let state = {
  user: readStoredUser(),
  accessToken: localStorage.getItem(appConfig.tokenStorageKey) || null,
  refreshToken: localStorage.getItem(appConfig.refreshTokenStorageKey) || null,
  // 'idle' -> not checked yet, 'loading' -> validating session,
  // 'authenticated' | 'unauthenticated'
  status: 'idle',
};

const listeners = new Set();
function emit() {
  listeners.forEach((listener) => listener());
}

export const authStore = {
  getSnapshot() {
    return state;
  },
  subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  setSession({ user, accessToken, refreshToken }) {
    state = { ...state, user, accessToken, refreshToken, status: 'authenticated' };
    localStorage.setItem(appConfig.authStorageKey, JSON.stringify(user));
    localStorage.setItem(appConfig.tokenStorageKey, accessToken);
    if (refreshToken) localStorage.setItem(appConfig.refreshTokenStorageKey, refreshToken);
    emit();
  },
  setTokens({ accessToken, refreshToken }) {
    state = { ...state, accessToken, refreshToken: refreshToken ?? state.refreshToken };
    localStorage.setItem(appConfig.tokenStorageKey, accessToken);
    if (refreshToken) localStorage.setItem(appConfig.refreshTokenStorageKey, refreshToken);
    emit();
  },
  setUser(user) {
    state = { ...state, user };
    localStorage.setItem(appConfig.authStorageKey, JSON.stringify(user));
    emit();
  },
  setStatus(status) {
    state = { ...state, status };
    emit();
  },
  clear() {
    state = { user: null, accessToken: null, refreshToken: null, status: 'unauthenticated' };
    localStorage.removeItem(appConfig.authStorageKey);
    localStorage.removeItem(appConfig.tokenStorageKey);
    localStorage.removeItem(appConfig.refreshTokenStorageKey);
    emit();
  },
};
