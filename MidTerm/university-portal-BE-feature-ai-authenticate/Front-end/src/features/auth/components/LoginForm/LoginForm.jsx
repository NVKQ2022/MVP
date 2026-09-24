import { useCallback, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ScanFace } from 'lucide-react';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog/dialog';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { redirectToHostWithSession } from '@/features/auth/utils/authRedirect';
import { env } from '@/config/env';
import { isEmailNotVerifiedError, getProblemDetail } from '@/utils/apiError';
import { FaceDetection } from '@/features/auth';

import './LoginForm.scss';

export function LoginForm() {
  const { login, faceLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const faceDetectionRef = useRef(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [faceDialogOpen, setFaceDialogOpen] = useState(false);
  const [liveFaceCount, setLiveFaceCount] = useState(0);
  const [faceSubmitting, setFaceSubmitting] = useState(false);
  const [faceError, setFaceError] = useState(null);

  const handleOpenFaceDialog = () => {
    setFaceError(null);
    setLiveFaceCount(0);
    setFaceDialogOpen(true);
  };

  const handleFaceDetected = useCallback((detections) => {
    setLiveFaceCount(detections.length);
  }, []);

  const handleFaceLogin = async () => {
    if (liveFaceCount !== 1) {
      setFaceError(
        liveFaceCount === 0
          ? 'No face detected. Please face the camera clearly.'
          : 'Multiple faces detected. Please make sure only one face is in the frame.'
      );
      return;
    }

    if (!faceDetectionRef.current) {
      setFaceError('Camera stream is not ready yet. Please wait a moment.');
      return;
    }

    setFaceSubmitting(true);
    setFaceError(null);

    try {
      // 1. Capture the cropped face image blob from webcam
      const faceBlob = await faceDetectionRef.current.captureCroppedFace();

      // 2. Prepare FormData matching .NET FaceAuthenticateLoginRequest
      const formData = new FormData();
      formData.append('Capture', faceBlob, 'face_capture.jpg');
      formData.append('DeviceId', navigator.userAgent || 'web-client');

      // 3. Authenticate with backend
      const { user, accessToken, refreshToken } = await faceLogin(formData);

      setFaceDialogOpen(false);

      if (user.role === 'Admin') {
        redirectToHostWithSession(env.adminHost, {
          accessToken,
          refreshToken,
        });
        return;
      }

      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err) {
      if (err?.response?.status === 401) {
        setFaceError('Face not recognized. Please adjust lighting and try again, or use your password.');
      } else {
        setFaceError(getProblemDetail(err) || err.message || 'Face authentication failed.');
      }
    } finally {
      setFaceSubmitting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const { user, accessToken, refreshToken } = await login({
        email,
        password,
      });

      if (user.role === 'Admin') {
        redirectToHostWithSession(env.adminHost, {
          accessToken,
          refreshToken,
        });
        return;
      }

      const from = location.state?.from?.pathname || '/';

      navigate(from, { replace: true });
    } catch (err) {
      if (isEmailNotVerifiedError(err)) {
        navigate('/verify-email', {
          replace: true,
          state: { email },
        });
        return;
      }

      if (err?.response?.status === 401) {
        setError('Invalid email or password.');
      } else {
        setError(getProblemDetail(err));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="login-form__field">
        <Label htmlFor="email">Email</Label>

        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="login-form__field">
        <Label htmlFor="password">Password</Label>

        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <div className="login-form__actions">
        <Button type="submit" className="login-form__submit" disabled={submitting}>
          {submitting ? 'Signing in...' : 'Login'}
        </Button>

        <Button
          type="button"
          variant="outline"
          className="login-form__face-btn"
          onClick={handleOpenFaceDialog}
        >
          <ScanFace className="login-form__face-btn-icon" />
          Face Login
        </Button>
      </div>

      <Dialog open={faceDialogOpen} onOpenChange={setFaceDialogOpen}>
        <DialogContent className="login-form__face-dialog">
          <DialogHeader>
            <DialogTitle>Face Login</DialogTitle>
            <DialogDescription>Place your face in the center of the frame to log in.</DialogDescription>
          </DialogHeader>

          {faceDialogOpen && (
            <FaceDetection
              ref={faceDetectionRef}
              className="login-form__face-detection"
              height={280}
              onFaceDetected={handleFaceDetected}
            />
          )}

          {faceError && (
            <Alert variant="destructive">
              <AlertDescription>{faceError}</AlertDescription>
            </Alert>
          )}

          <Button
            type="button"
            className="login-form__face-submit"
            disabled={liveFaceCount === 0 || faceSubmitting}
            onClick={handleFaceLogin}
          >
            {faceSubmitting ? 'Verifying...' : 'Capture & Sign in'}
          </Button>
        </DialogContent>
      </Dialog>
    </form>
  );
}