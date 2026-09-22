import { useParams, useNavigate } from 'react-router-dom';

import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';
import {
  mockUsers,
  checkUserPassword,
  getUserByEmail,
  getUserById,
} from '@/features/users/mock-data';
import AdminActions from './UserActions';
import UserHeader from './UserHeader';
import DetailInformation from './UserInformation';
// uesr model
// {
// id: 'u1',
// name: 'Nguyen Van A',
// email: 'nguyenvana@eduportal.vn',
// password: 'eduportal',
// role: 'Student',
// status: 'active',
// createdAt: '2026-01-12',
// }

function BackButton() {
  const navigate = useNavigate();

  return (
    <Button
      className="cursor-pointer hover:bg-muted"
      variant="outline"
      size="sm"
      onClick={() => navigate(-1)}
    >
      ← Back
    </Button>
  );
}

export default function AdminUserDetail() {
  const { id: userId } = useParams();
  const navigate = useNavigate();

  const user = getUserById(userId);

  if (!user) {
    return (
      <div className="space-y-6 p-8">
        <BackButton />

        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-semibold">Invalid name</h1>

                <p className="mt-1 text-sm text-muted-foreground">invalid.email@example.com</p>
              </div>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">No user with ID: {userId}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <BackButton />

      <UserHeader user={user} />
      <DetailInformation user={user} />
      <AdminActions user={user} />
    </div>
  );
}
