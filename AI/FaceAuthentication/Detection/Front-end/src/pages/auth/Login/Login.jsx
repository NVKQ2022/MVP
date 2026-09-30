import { Link, useLocation } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card/card';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import { LoginForm } from '@/features/auth';
import { getAppDomain } from '@/routes/getAppDomain';

import './Login.scss';

export default function Login() {
  const location = useLocation();

  const justVerified = location.state?.verified;
  const canSignUp = getAppDomain() !== 'admin';

  return (
    <Card className="login-card">
      <CardHeader className="login-card__header">
        <LogIn className="login-card__icon" />
        <CardTitle>Sign in</CardTitle>
      </CardHeader>

      <CardContent className="login-card__content">
        {justVerified && (
          <Alert>
            <AlertDescription>Email verified - you can now sign in.</AlertDescription>
          </Alert>
        )}

        <LoginForm />

        {canSignUp && (
          <p className="login-card__footer">
            Don't have an account?{' '}
            <Link to="/signup" className="login-card__link">
              Sign up
            </Link>
          </p>
        )}
      </CardContent>
    </Card>
  );
}
