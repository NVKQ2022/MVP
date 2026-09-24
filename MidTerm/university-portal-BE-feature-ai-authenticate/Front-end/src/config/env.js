export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  studentHost: import.meta.env.VITE_STUDENT_HOST || 'localhost',
  adminHost: import.meta.env.VITE_ADMIN_HOST || 'admin.localhost',
  mode: import.meta.env.MODE,
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
};
