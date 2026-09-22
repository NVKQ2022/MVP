import { Badge } from '@/components/ui/badge/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';

export default function DetailInformation({ user }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Detail information</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <p className="text-sm text-muted-foreground">User ID</p>
            <p className="mt-1 font-medium">{user.id}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Name</p>
            <p className="mt-1 font-medium">{user.name}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="mt-1 font-medium">{user.email}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Status</p>

            <div className="mt-1">
              <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                {user.status}
              </Badge>
            </div>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Created at</p>
            <p className="mt-1 font-medium">{user.createdAt}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Role</p>
            <p className="mt-1 font-medium">{user.role}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
