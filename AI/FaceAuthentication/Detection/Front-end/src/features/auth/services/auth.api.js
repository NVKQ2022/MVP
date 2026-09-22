import { checkUserPassword } from '@/features/users/mock-data';

export function loginRequest({ email, password }) {
  const user = checkUserPassword(email, password);

  if (!user) {
    return Promise.resolve({
      success: false,
      message: 'Username or password is incorrect',
    });
  }

  if (user.status === 'locked') {
    return Promise.resolve({
      success: false,
      message: 'Your account is locked',
    });
  }

  if (user.status === 'inactive') {
    return Promise.resolve({
      success: false,
      message: 'Your account is inactive',
    });
  }

  if (user.status === 'pending') {
    return Promise.resolve({
      success: false,
      message: 'Your account is pending approval',
    });
  }

  return Promise.resolve({
    success: true,
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role.toLowerCase(),
    },
    token: 'mock-token',
  });
}
