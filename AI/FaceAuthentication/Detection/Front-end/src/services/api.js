import axios from 'axios';
import { env } from '@/config/env';
import { appConfig } from '@/config/appConfig';

const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Future: attach Authorization header once real auth exists.
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(appConfig.tokenStorageKey);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Future: centralize error handling (401 redirect, toast, refresh token, etc.)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Placeholder for future global error handling.
    return Promise.reject(error);
  },
);

export default apiClient;
