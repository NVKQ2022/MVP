import { useEffect, useRef, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card/card';
import { Button } from '@/components/ui/button/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog/dialog';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { FaceDetection, useAuth } from '@/features/auth';
import { authApi } from '@/features/auth/services/auth.api';
import { toast } from '@/components/common/Toaster/toast';
import styles from './Settings.module.scss';

const MFA_ACTION_COOLDOWN_MS = 1500;

export function StudentSettings() {
  const { user, updateUser } = useAuth();
  const faceDetectionRef = useRef(null);
  const [isSetupOpen, setIsSetupOpen] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureError, setCaptureError] = useState(null);

  const [isMfaEnabled, setIsMfaEnabled] = useState(() => Boolean(user?.requiresMfa));
  const [isMfaLoading, setIsMfaLoading] = useState(false);
  const [isMfaDelaying, setIsMfaDelaying] = useState(false);
  const [isDisableConfirmOpen, setIsDisableConfirmOpen] = useState(false);
  const mfaDelayTimeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (mfaDelayTimeoutRef.current) {
        clearTimeout(mfaDelayTimeoutRef.current);
      }
    };
  }, []);

  const delayBeforeMfaAction = () => {
    setIsMfaDelaying(true);
    return new Promise((resolve) => {
      mfaDelayTimeoutRef.current = setTimeout(() => {
        setIsMfaDelaying(false);
        resolve();
      }, MFA_ACTION_COOLDOWN_MS);
    });
  };

  const handleSetupFaceRecognition = () => {
    setCaptureError(null);
    setIsSetupOpen(true);
  };

  const handleCapture = async (capturedBlob = null) => {
    if (isCapturing) return;
    setCaptureError(null);
    setIsCapturing(true);
    try {
      // Ingest the WHOLE uncropped camera frame (required for backend liveness & anti-spoofing)
      const blob = capturedBlob || (await faceDetectionRef.current?.captureFullFrame());
      if (!blob) throw new Error('No face captured. Please position your face in the center.');

      const formData = new FormData();
      formData.append('faceImage', blob, 'face.jpg');
      await authApi.faceRegister(formData);

      setIsSetupOpen(false);
    } catch (err) {
      setCaptureError(err instanceof Error ? err.message : 'Failed to capture face');
      faceDetectionRef.current?.resetCooldown();
    } finally {
      setIsCapturing(false);
    }
  };

  const handleRetryOrCapture = () => {
    if (captureError) {
      setCaptureError(null);
      faceDetectionRef.current?.resetCooldown();
      return;
    }
    handleCapture();
  };

  const handleEnableMfa = async () => {
    await delayBeforeMfaAction();
    setIsMfaLoading(true);
    try {
      await authApi.enableMfa();
      setIsMfaEnabled(true);
      updateUser({ requiresMfa: true });
    } catch (err) {
      toast.error('Failed to enable MFA', {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setIsMfaLoading(false);
    }
  };

  const handleDisableMfa = async () => {
    await delayBeforeMfaAction();
    setIsMfaLoading(true);
    try {
      await authApi.disableMfa();
      setIsMfaEnabled(false);
      updateUser({ requiresMfa: false });
    } catch (err) {
      toast.error('Failed to disable MFA', {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setIsMfaLoading(false);
    }
  };

  return (
    <div className={styles.settings_wrapper}>
      <Card>
        <CardContent className={styles.settings_row}>
          <div className={styles.settings_info}>
            <h2 className={styles.settings_title}>Set up Face Recognition for account</h2>
            <p className={styles.settings_description}>
              Add Face Recognition as a login method for your account. Once set up, you can sign in
              or confirm sensitive actions by scanning your face on trusted devices, instead of
              typing your password every time.
            </p>
          </div>
          <Button onClick={handleSetupFaceRecognition}>Setup</Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent className={styles.settings_row}>
          <div className={styles.settings_info}>
            <h2 className={styles.settings_title}>Enable Multi-Factor Authentication</h2>
            <p className={styles.settings_description}>
              Add an extra layer of security to your account. Once enabled, you'll need to verify
              your identity with a second factor in addition to your password when signing in or
              confirming sensitive actions.
            </p>
          </div>
          <Button
            variant={isMfaEnabled ? 'outline' : 'default'}
            onClick={isMfaEnabled ? () => setIsDisableConfirmOpen(true) : handleEnableMfa}
            disabled={isMfaLoading || isMfaDelaying}
          >
            {isMfaDelaying
              ? '...'
              : isMfaLoading
                ? isMfaEnabled
                  ? 'Disabling...'
                  : 'Enabling...'
                : isMfaEnabled
                  ? 'Disable'
                  : 'Enable'}
          </Button>
        </CardContent>
      </Card>

      <Dialog open={isSetupOpen} onOpenChange={setIsSetupOpen}>
        <DialogContent className={styles.setup_dialog}>
          <DialogHeader>
            <DialogTitle>Set up Face Recognition</DialogTitle>
            <DialogDescription>
              Position your face in the center of the camera frame to automatically capture, or press Capture.
            </DialogDescription>
          </DialogHeader>

          <FaceDetection
            ref={faceDetectionRef}
            height={320}
            onFaceCentered={handleCapture}
            autoCaptureOnCenter={!captureError && !isCapturing}
          />

          {captureError && <p className={styles.setup_error}>{captureError}</p>}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsSetupOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleRetryOrCapture}
              disabled={isCapturing}
              variant={captureError ? 'secondary' : 'default'}
            >
              {isCapturing ? 'Registering...' : captureError ? 'Try Again' : 'Capture'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={isDisableConfirmOpen}
        onOpenChange={setIsDisableConfirmOpen}
        title="Disable Multi-Factor Authentication?"
        description="You won't be asked for a second factor anymore when signing in or confirming sensitive actions. You can enable it again anytime."
        confirmLabel="Disable"
        variant="destructive"
        onConfirm={handleDisableMfa}
      />
    </div>
  );
}