import { Button } from '@/components/ui/button/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';

export default function AdminActions({ user }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Actions</CardTitle>
      </CardHeader>

      <CardContent>
        <Button variant={user.status === 'active' ? 'destructive' : 'secondary'}>
          {user.status === 'Active' ? 'Deactivate account' : 'Activate account'}
        </Button>
      </CardContent>
    </Card>
  );
}
