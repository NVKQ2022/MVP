import { Badge } from '@/components/ui/badge/badge';
import { Card, CardContent } from '@/components/ui/card/card';

export default function UserHeader({ user }) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{user.name}</h1>

            <p className="mt-1 text-sm text-muted-foreground">{user.email}</p>
          </div>

          <Badge variant={user.status === 'Active' ? 'default' : 'secondary'}>{user.status}</Badge>
        </div>

        <p className="mt-4 text-sm text-muted-foreground">User ID: {user.id}</p>
      </CardContent>
    </Card>
  );
}
