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
  setUser(user) {
    state = { ...state, user };
    if (user) {
      localStorage.setItem(appConfig.authStorageKey, JSON.stringify(user));
      localStorage.setItem(appConfig.tokenStorageKey, 'mock-token');
    } else {
      localStorage.removeItem(appConfig.authStorageKey);
      localStorage.removeItem(appConfig.tokenStorageKey);
    }
    emit();
  },
  clear() {
    authStore.setUser(null);
  },
};
