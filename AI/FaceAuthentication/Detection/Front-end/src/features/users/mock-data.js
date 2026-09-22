export const mockUsers = [
  {
    id: 'u1',
    name: 'Nguyen Van A',
    email: 'nguyenvana@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'active',
    createdAt: '2026-01-12',
  },
  {
    id: 'u2',
    name: 'Tran Thi B',
    email: 'tranthib@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'active',
    createdAt: '2026-01-15',
  },
  {
    id: 'u3',
    name: 'Le Van C',
    email: 'levanc@eduportal.vn',
    password: 'eduportal',
    role: 'Admin',
    status: 'active',
    createdAt: '2025-11-02',
  },
  {
    id: 'u4',
    name: 'Pham Thi D',
    email: 'phamthid@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'locked',
    createdAt: '2026-02-20',
  },
  {
    id: 'u5',
    name: 'Hoang Van E',
    email: 'hoangvane@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'pending',
    createdAt: '2026-03-05',
  },
  {
    id: 'u6',
    name: 'Vu Thi F',
    email: 'vuthif@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'inactive',
    createdAt: '2025-09-18',
  },
  {
    id: 'u7',
    name: 'Dang Van G',
    email: 'dangvang@eduportal.vn',
    password: 'eduportal',
    role: 'Admin',
    status: 'active',
    createdAt: '2025-08-30',
  },
  {
    id: 'u8',
    name: 'Bui Thi H',
    email: 'buithih@eduportal.vn',
    password: 'eduportal',
    role: 'Student',
    status: 'active',
    createdAt: '2026-04-11',
  },
];

export function getUserById(id) {
  return mockUsers.find((u) => u.id === id);
}

export function getUserByEmail(email) {
  return mockUsers.find((u) => u.email === email);
}

export function checkUserPassword(email, pwd) {
  return mockUsers.find((u) => u.email === email && u.password === pwd);
}
