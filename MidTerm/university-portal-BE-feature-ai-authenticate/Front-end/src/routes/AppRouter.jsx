import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { getAppDomain } from './getAppDomain';
import { studentRoutes } from './student.routes';
import { adminRoutes } from './admin.routes';
import { authRoutes } from './auth.routes';
import { rootRoutes } from './root.routes';

function buildRoutes() {
  const domain = getAppDomain();

  if (domain === 'admin') {
    return [...adminRoutes, ...authRoutes];
  }

  if (domain === 'student') {
    return [...studentRoutes, ...authRoutes];
  }

  return [...rootRoutes];
}

const router = createBrowserRouter(buildRoutes());

export function AppRouter() {
  return <RouterProvider router={router} />;
}
