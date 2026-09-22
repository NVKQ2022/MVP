import InvalidDomain from '@/pages/errors/InvalidDomain';

// Rendered only when getAppDomain() returns "unknown".
export const rootRoutes = [
  {
    path: '*',
    element: <InvalidDomain />,
  },
];
