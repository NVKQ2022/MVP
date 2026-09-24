import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { getProblemDetail } from '@/utils/apiError';

import './VerifyEmailForm.scss';

const RESEND_COOLDOWN_SECONDS = 30;

export function VerifyEmailForm() {
  const { verifyEmail, resendOtp } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState(location.state?.email || '');
  const [otp, setOtp] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [resendState, setResendState] = useState({
    sending: false,
    cooldown: 0,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await verifyEmail({ email, otp });
      setSuccess(true);

      setTimeout(() => {
        navigate('/login', {
          replace: true,
          state: { verified: true },
        });
      }, 1500);
    } catch (err) {
      setError(getProblemDetail(err) || 'Invalid or expired code. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!email || resendState.cooldown > 0) return;

    setResendState({
      sending: true,
      cooldown: 0,
    });

    try {
      await resendOtp(email);

      setResendState({
        sending: false,
        cooldown: RESEND_COOLDOWN_SECONDS,
      });

      const interval = setInterval(() => {
        setResendState((prev) => {
          if (prev.cooldown <= 1) {
            clearInterval(interval);

            return {
              ...prev,
              cooldown: 0,
            };
          }

          return {
            ...prev,
            cooldown: prev.cooldown - 1,
          };
        });
      }, 1000);
    } catch {
      setResendState({
        sending: false,
        cooldown: 0,
      });

      setError('Could not resend the code. Please try again shortly.');
    }
  };

  if (success) {
    return (
      <Alert>
        <AlertDescription>Your email has been verified. Redirecting to sign in…</AlertDescription>
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="verify-email-form">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="verify-email-form__field">
        <Label htmlFor="email">Email</Label>

        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          readOnly={!!location.state?.email}
        />
      </div>

      <div className="verify-email-form__field">
        <Label htmlFor="otp">Verification Code</Label>

        <Input
          id="otp"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          placeholder="Enter the code sent to your email"
          inputMode="numeric"
          autoComplete="one-time-code"
          required
        />
      </div>

      <Button type="submit" className="verify-email-form__submit" disabled={submitting}>
        {submitting ? 'Verifying...' : 'Verify Email'}
      </Button>

      <Button
        type="button"
        variant="link"
        className="verify-email-form__resend"
        onClick={handleResend}
        disabled={resendState.sending || resendState.cooldown > 0 || !email}
      >
        {resendState.cooldown > 0
          ? `Resend code (${resendState.cooldown}s)`
          : resendState.sending
            ? 'Sending...'
            : "Didn't get a code? Resend"}
      </Button>
    </form>
  );
}
