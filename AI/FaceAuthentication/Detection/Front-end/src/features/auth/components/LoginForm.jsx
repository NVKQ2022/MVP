import { useState } from 'react';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import { Separator } from '@/components/ui/separator/separator';
import { useLogin } from '@/features/auth/hooks/useLogin';
import { FaceDetection } from '@/features/auth/components/FaceDetection';
import { env } from '@/config/env';
import { ScanFace, ArrowLeft, CheckCircle2 } from 'lucide-react';

export function LoginForm() {
  const { login } = useLogin();

  const [isFaceAuth, setIsFaceAuth] = useState(false);
  const [detectedFaces, setDetectedFaces] = useState([]);
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

  if (isFaceAuth) {
    const primaryFace = detectedFaces[0];
    const confidenceScore = primaryFace?.categories?.[0]?.score;

    return (
      <div className="space-y-4">
        <div className="text-center space-y-1">
          <p className="text-sm font-medium text-foreground">Face Detection</p>
          <p className="text-xs text-muted-foreground">
            Look directly at the camera for face recognition
          </p>
        </div>

        {/* MediaPipe BlazeFace Camera Feed */}
        <div className="w-full">
          <FaceDetection
            height={260}
            minConfidence={0.5}
            mirrored={true}
            onFaceDetected={(faces) => setDetectedFaces(faces)}
          />
        </div>

        {/* Live Feedback */}
        {detectedFaces.length > 0 ? (
          <div className="flex items-center justify-center gap-2 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-600 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>
              Face detected ({confidenceScore ? `${(confidenceScore * 100).toFixed(0)}%` : 'Active'})
            </span>
          </div>
        ) : (
          <div className="text-center text-xs text-muted-foreground py-1">
            Position your face inside the camera view
          </div>
        )}

        {/* Back to password login button */}
        <Button
          type="button"
          variant="outline"
          className="w-full flex items-center justify-center gap-2"
          onClick={() => {
            setIsFaceAuth(false);
            setDetectedFaces([]);
          }}
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Password Login
        </Button>
      </div>
    );
  }

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

      {/* Face Authenticate Button */}
      <Button
        type="button"
        variant="outline"
        className="w-full flex items-center justify-center gap-2 border-primary/40 hover:bg-primary/5 text-primary"
        onClick={() => setIsFaceAuth(true)}
      >
        <ScanFace className="w-4 h-4" />
        Face authenticate
      </Button>

      <div className="relative flex items-center justify-center">
        <Separator className="w-full" />
        <span className="absolute bg-card px-2 text-xs text-muted-foreground">OR</span>
      </div>

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
