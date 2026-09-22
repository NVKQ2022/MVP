import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card/card';
import { GraduationCap } from 'lucide-react';
import { LoginForm } from '@/features/auth';

export default function Login() {
  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="items-center text-center">
        <GraduationCap className="mb-2 h-8 w-8 text-primary" />
        <CardTitle>Sign in</CardTitle>
      </CardHeader>
      <CardContent>
        <LoginForm />
      </CardContent>
    </Card>
  );
}
