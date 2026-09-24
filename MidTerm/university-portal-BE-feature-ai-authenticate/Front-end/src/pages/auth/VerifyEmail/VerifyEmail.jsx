import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card/card';
import { MailCheck } from 'lucide-react';
import { VerifyEmailForm } from '@/features/auth';

import './VerifyEmail.scss';

export default function VerifyEmail() {
  return (
    <Card className="verify-email-card">
      <CardHeader className="verify-email-card__header">
        <MailCheck className="verify-email-card__icon" />

        <CardTitle>Verify your email</CardTitle>

        <CardDescription>Enter the code we sent to your inbox</CardDescription>
      </CardHeader>

      <CardContent>
        <VerifyEmailForm />
      </CardContent>
    </Card>
  );
}
