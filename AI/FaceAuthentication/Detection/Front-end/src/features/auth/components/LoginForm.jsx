import { useState } from 'react';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import { useLogin } from '@/features/auth/hooks/useLogin';
import { env } from '@/config/env';

export function LoginForm() {
  const { login } = useLogin();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError('');
    setSubmitting(true);

    try {
      const user = await login({ email, password });

      const port = window.location.port ? `:${window.location.port}` : '';

      if (user.role === 'admin') {
        window.location.assign(`http://${env.adminHost}${port}/`);
      } else {
        window.location.assign(`http://${env.studentHost}${port}/`);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Unable to sign in. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2 flex flex-col">
        <Label htmlFor="email">account</Label>
        <span>Admin: levanc@eduportal.vn</span>
        <span>Student: nguyenvana@eduportal.vn</span>
      </div>

      <div className="space-y-2 flex flex-col">
        <Label htmlFor="email">Password</Label>
        <span>eduportal</span>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>

        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setError('');
          }}
          placeholder="Enter your email"
          disabled={submitting}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>

        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            setError('');
          }}
          placeholder="Enter your password"
          disabled={submitting}
          required
        />
      </div>

      <Button type="submit" className="w-full" disabled={submitting}>
        {submitting ? 'Signing in...' : 'Login'}
      </Button>
    </form>
  );
}
