import { Link } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card/card';
import { GraduationCap } from 'lucide-react';
import { RegisterForm } from '@/features/auth';

import './Signup.scss';

export default function Signup() {
  return (
    <Card className="signup-card">
      <CardHeader className="signup-card__header">
        <GraduationCap className="signup-card__icon" />

        <CardTitle>Create your account</CardTitle>

        <CardDescription>Sign up with your student email</CardDescription>
      </CardHeader>

      <CardContent className="signup-card__content">
        <RegisterForm />

        <p className="signup-card__login">
          Already have an account?{' '}
          <Link to="/login" className="signup-card__login-link">
            Sign in
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
