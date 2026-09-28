import { useEffect, useRef, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import { FilesetResolver, FaceDetector } from '@mediapipe/tasks-vision';
import { Camera, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { appConfig } from '@/config/appConfig';
import './FaceDetection.scss';

/**
 * Draws a rounded rectangle path on canvas with cross-browser compatibility.
 */
function drawRoundRect(ctx, x, y, w, h, r) {
  if (ctx.roundRect) {
    ctx.roundRect(x, y, w, h, r);
    return;
  }
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y, x + r, y, r);
}

/**
 * Evaluates whether the primary detected face is positioned in the middle of the video frame.
 */
function evaluateFaceCentering(detections, frameWidth, frameHeight) {
  if (!detections || detections.length === 0) {
    return {
      isCentered: false,
      reason: 'no_face',
      message: 'Position your face in the camera',
      face: null,
    };
  }

  if (detections.length > 1) {
    return {
      isCentered: false,
      reason: 'multiple_faces',
      message: 'Multiple faces detected — ensure only 1 person is in frame',
      face: null,
    };
  }

  const detection = detections[0];
  const { originX, originY, width: boxW, height: boxH } = detection.boundingBox;
  const faceCenterX = originX + boxW / 2;
  const faceCenterY = originY + boxH / 2;

  const frameCenterX = frameWidth / 2;
  const frameCenterY = frameHeight / 2;

  // Normalized distance from center
  const dx = Math.abs(faceCenterX - frameCenterX) / frameWidth;
  const dy = Math.abs(faceCenterY - frameCenterY) / frameHeight;
  const boxRatio = boxW / frameWidth;

  // Horizontal tolerance: within +/- 13% of center
  const isHorizontallyCentered = dx <= 0.13;
  // Vertical tolerance: within +/- 15% of center
  const isVerticallyCentered = dy <= 0.15;
  // Size bounds: ensure user is neither too distant nor pressed against the lens
  const isGoodSize = boxRatio >= 0.15 && boxRatio <= 0.65;

  let message = 'Face centered! Hold still...';
  let isCentered = false;

  if (boxRatio < 0.15) {
    message = 'Move closer to the camera';
  } else if (boxRatio > 0.65) {
    message = 'Move slightly back from camera';
  } else if (!isHorizontallyCentered) {
    message = 'Align your face in the center';
  } else if (!isVerticallyCentered) {
    message = 'Align your face in the center';
  } else {
    isCentered = true;
  }

  return {
    isCentered,
    reason: isCentered ? 'centered' : 'off_center',
    message,
    face: detection,
    dx,
    dy,
    boxRatio,
  };
}

/**
 * Draws the central biometric viewfinder guide, corner brackets, and hold progress.
 */
function drawCenterGuideOverlay(ctx, width, height, isCentered, holdProgress, themeColor) {
  const guideW = Math.min(width * 0.44, 340);
  const guideH = Math.min(height * 0.60, 440);
  const guideX = (width - guideW) / 2;
  const guideY = (height - guideH) / 2;
  const cornerLen = 28;
  const guideRadius = 24;

  ctx.save();

  // Guide bounding box
  const guideColor = isCentered ? '#10b981' : 'rgba(255, 255, 255, 0.35)';
  ctx.strokeStyle = guideColor;
  ctx.lineWidth = isCentered ? 3 : 1.5;

  if (isCentered) {
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 14;
  }

  ctx.beginPath();
  drawRoundRect(ctx, guideX, guideY, guideW, guideH, guideRadius);
  ctx.stroke();

  // Corner brackets
  ctx.lineWidth = 4;
  ctx.strokeStyle = isCentered ? '#34d399' : themeColor;

  // Top-Left
  ctx.beginPath();
  ctx.moveTo(guideX, guideY + cornerLen);
  ctx.lineTo(guideX, guideY + guideRadius);
  ctx.arcTo(guideX, guideY, guideX + guideRadius, guideY, guideRadius);
  ctx.lineTo(guideX + cornerLen, guideY);
  ctx.stroke();

  // Top-Right
  ctx.beginPath();
  ctx.moveTo(guideX + guideW - cornerLen, guideY);
  ctx.lineTo(guideX + guideW - guideRadius, guideY);
  ctx.arcTo(guideX + guideW, guideY, guideX + guideW, guideY + guideRadius, guideRadius);
  ctx.lineTo(guideX + guideW, guideY + cornerLen);
  ctx.stroke();

  // Bottom-Left
  ctx.beginPath();
  ctx.moveTo(guideX, guideY + guideH - cornerLen);
  ctx.lineTo(guideX, guideY + guideH - guideRadius);
  ctx.arcTo(guideX, guideY + guideH, guideX + guideRadius, guideY + guideH, guideRadius);
  ctx.lineTo(guideX + cornerLen, guideY + guideH);
  ctx.stroke();

  // Bottom-Right
  ctx.beginPath();
  ctx.moveTo(guideX + guideW - cornerLen, guideY + guideH);
  ctx.lineTo(guideX + guideW - guideRadius, guideY + guideH);
  ctx.arcTo(guideX + guideW, guideY + guideH, guideX + guideW, guideY + guideH - guideRadius, guideRadius);
  ctx.lineTo(guideX + guideW, guideY + guideH - cornerLen);
  ctx.stroke();

  // Draw hold progress bar at top of guide
  if (isCentered && holdProgress > 0) {
    ctx.fillStyle = 'rgba(15, 23, 42, 0.6)';
    ctx.fillRect(guideX, guideY - 14, guideW, 6);
    ctx.fillStyle = '#10b981';
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 8;
    ctx.fillRect(guideX, guideY - 14, guideW * holdProgress, 6);
  }

  ctx.restore();
}

export const FaceDetection = forwardRef(function FaceDetection(
  {
    onFaceDetected,
    onFaceCentered,
    autoCaptureOnCenter = true,
    centerHoldDurationMs = appConfig.faceAuth?.centerHoldDurationMs ?? 800,
    cooldownMs = appConfig.faceAuth?.cooldownMs ?? 2500,
    minConfidence = appConfig.faceAuth?.minDetectionConfidence ?? 0.5,
    mirrored = true,
    showOverlay = true,
    showCenterGuide = true,
    themeColor = '#0284c7',
    width = '100%',
    height = 360,
    className = '',
    style = {},
  },
  ref
) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectorRef = useRef(null);
  const requestRef = useRef(null);
  const latestDetectionRef = useRef(null);
  const latestCenterStatusRef = useRef(null);
  const centeredSinceRef = useRef(null);
  const isLockedRef = useRef(false);
  const lastCaptureTimeRef = useRef(0);
  const onFaceCenteredRef = useRef(onFaceCentered);
  const onFaceDetectedRef = useRef(onFaceDetected);

  // Keep callback refs updated to avoid re-triggering requestAnimationFrame loop
  useEffect(() => {
    onFaceCenteredRef.current = onFaceCentered;
  }, [onFaceCentered]);

  useEffect(() => {
    onFaceDetectedRef.current = onFaceDetected;
  }, [onFaceDetected]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faceCount, setFaceCount] = useState(0);
  const [isCenteredState, setIsCenteredState] = useState(false);
  const [guidanceMessage, setGuidanceMessage] = useState('Position your face in the camera');
  const [isFlashing, setIsFlashing] = useState(false);

  // Initialize MediaPipe BlazeFace Detector
  useEffect(() => {
    let isCancelled = false;

    async function initMediaPipe() {
      try {
        setIsLoading(true);
        setError(null);

        const vision = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
        );

        if (isCancelled) return;

        const detector = await FaceDetector.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite',
            delegate: 'GPU',
          },
          runningMode: 'VIDEO',
          minDetectionConfidence: minConfidence,
        });

        if (isCancelled) {
          detector.close();
          return;
        }

        detectorRef.current = detector;
        setIsLoading(false);
      } catch (err) {
        if (isCancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to load MediaPipe model');
        setIsLoading(false);
      }
    }

    initMediaPipe();

    return () => {
      isCancelled = true;
      if (detectorRef.current) {
        detectorRef.current.close();
        detectorRef.current = null;
      }
    };
  }, [minConfidence]);

  // Initialize Camera Stream
  useEffect(() => {
    let isCancelled = false;
    let stream = null;

    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user',
          },
          audio: false,
        });

        if (isCancelled) {
          mediaStream.getTracks().forEach((track) => track.stop());
          return;
        }

        stream = mediaStream;
        const video = videoRef.current;

        if (video) {
          video.srcObject = mediaStream;
          video.onloadedmetadata = async () => {
            if (isCancelled || !videoRef.current) return;
            try {
              await video.play();
            } catch (playErr) {
              if (!isCancelled && playErr instanceof Error && playErr.name !== 'AbortError') {
                setError(playErr.message);
              }
            }
          };
        }
      } catch (err) {
        if (isCancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to access camera');
      }
    }

    startCamera();

    return () => {
      isCancelled = true;
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      if (videoRef.current) {
        videoRef.current.onloadedmetadata = null;
        videoRef.current.srcObject = null;
      }
    };
  }, []);

  /**
   * Captures the entire, uncropped video frame into a JPEG blob.
   * This whole image is required by the backend liveness & anti-spoofing pipeline.
   */
  const captureFullFrameBlob = useCallback(() => {
    return new Promise((resolve, reject) => {
      const video = videoRef.current;
      if (!video || video.readyState < 2) {
        return reject(new Error('Camera stream is not ready yet. Please wait.'));
      }

      const width = video.videoWidth;
      const height = video.videoHeight;
      if (!width || !height) {
        return reject(new Error('Video dimensions unavailable.'));
      }

      const offscreen = document.createElement('canvas');
      offscreen.width = width;
      offscreen.height = height;
      const ctx = offscreen.getContext('2d');
      if (!ctx) {
        return reject(new Error('Failed to create canvas context'));
      }

      // Draw the entire uncropped video frame
      ctx.drawImage(video, 0, 0, width, height);

      offscreen.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create image blob'));
          }
        },
        'image/jpeg',
        0.95
      );
    });
  }, []);

  const triggerFlash = useCallback(() => {
    setIsFlashing(true);
    setTimeout(() => setIsFlashing(false), 300);
  }, []);

  // Frame detection loop
  const predictLoop = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const detector = detectorRef.current;

    if (video && canvas && detector && video.readyState >= 2 && !video.paused) {
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }

      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const startTimeMs = performance.now();
        const result = detector.detectForVideo(video, startTimeMs);
        const detections = result.detections || [];
        latestDetectionRef.current = detections[0] ?? null;

        setFaceCount(detections.length);
        if (onFaceDetectedRef.current) {
          onFaceDetectedRef.current(detections);
        }

        // Evaluate whether face is positioned in the middle of the frame
        const centerStatus = evaluateFaceCentering(detections, canvas.width, canvas.height);
        latestCenterStatusRef.current = centerStatus;

        setGuidanceMessage((prev) => (prev !== centerStatus.message ? centerStatus.message : prev));
        setIsCenteredState((prev) => (prev !== centerStatus.isCentered ? centerStatus.isCentered : prev));

        let holdProgress = 0;
        const now = performance.now();
        const isCaptureEnabled = autoCaptureOnCenter && Boolean(onFaceCenteredRef.current);

        if (centerStatus.isCentered) {
          if (isCaptureEnabled) {
            if (centeredSinceRef.current === null) {
              centeredSinceRef.current = now;
            }
            const elapsed = now - centeredSinceRef.current;
            holdProgress = Math.min(1.0, elapsed / centerHoldDurationMs);

            if (holdProgress >= 1.0 && !isLockedRef.current) {
              isLockedRef.current = true;
              lastCaptureTimeRef.current = now;
              triggerFlash();

              captureFullFrameBlob()
                .then((fullFrameBlob) => {
                  if (onFaceCenteredRef.current) {
                    onFaceCenteredRef.current(fullFrameBlob, centerStatus);
                  }
                })
                .catch((err) => {
                  console.error('Auto-capture full frame error:', err);
                  isLockedRef.current = false;
                });
            }
          } else {
            // When auto-capture is paused (e.g. after non-200 response, waiting for user to click Try Again)
            centeredSinceRef.current = null;
            holdProgress = 0;
            setGuidanceMessage('Face inside box. Click "Try Again" to retry');
          }
        } else {
          centeredSinceRef.current = null;
          // Unlock after cooldown elapsed
          if (isLockedRef.current && now - lastCaptureTimeRef.current > cooldownMs) {
            isLockedRef.current = false;
          }
        }

        // Draw Center Viewfinder Guide Overlay
        if (showCenterGuide) {
          drawCenterGuideOverlay(
            ctx,
            canvas.width,
            canvas.height,
            centerStatus.isCentered,
            holdProgress,
            themeColor
          );
        }

        // Draw Face Bounding Box & Keypoints
        if (showOverlay && detections.length > 0) {
          detections.forEach((detection) => {
            const { originX, originY, width: boxWidth, height: boxHeight } = detection.boundingBox;
            const score = detection.categories?.[0]?.score ?? 0;
            const x = mirrored ? canvas.width - originX - boxWidth : originX;
            const activeColor = centerStatus.isCentered ? '#10b981' : themeColor;

            // Draw bounding box
            ctx.save();
            ctx.strokeStyle = activeColor;
            ctx.lineWidth = centerStatus.isCentered ? 3.5 : 2.5;
            if (centerStatus.isCentered) {
              ctx.shadowColor = '#10b981';
              ctx.shadowBlur = 12;
            }
            ctx.strokeRect(x, originY, boxWidth, boxHeight);

            // Draw score pill
            const label = centerStatus.isCentered
              ? `Centered: ${(score * 100).toFixed(0)}%`
              : `Face: ${(score * 100).toFixed(0)}%`;
            ctx.font = 'bold 13px sans-serif';
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
            ctx.fillRect(x, Math.max(0, originY - 24), textWidth + 14, 22);
            ctx.fillStyle = centerStatus.isCentered ? '#34d399' : '#ffffff';
            ctx.fillText(label, x + 7, Math.max(16, originY - 8));

            // Draw 6 BlazeFace Keypoints
            if (detection.keypoints) {
              detection.keypoints.forEach((kp) => {
                const kx = mirrored ? canvas.width - kp.x * canvas.width : kp.x * canvas.width;
                const ky = kp.y * canvas.height;

                ctx.beginPath();
                ctx.arc(kx, ky, 4, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = activeColor;
                ctx.shadowBlur = 8;
                ctx.fill();
              });
            }
            ctx.restore();
          });
        }
      }
    }

    requestRef.current = requestAnimationFrame(predictLoop);
  }, [
    mirrored,
    showOverlay,
    showCenterGuide,
    themeColor,
    centerHoldDurationMs,
    cooldownMs,
    autoCaptureOnCenter,
    captureFullFrameBlob,
    triggerFlash,
  ]);

  useEffect(() => {
    if (!isLoading && !error) {
      requestRef.current = requestAnimationFrame(predictLoop);
    }
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [isLoading, error, predictLoop]);

  useImperativeHandle(
    ref,
    () => ({
      // Both captureFullFrame and captureWholeImage return the entire uncropped image
      captureFullFrame: () => captureFullFrameBlob(),
      captureWholeImage: () => captureFullFrameBlob(),
      // Redirect captureCroppedFace to whole image to protect backend liveness & FAS models
      captureCroppedFace: () => captureFullFrameBlob(),
      isFaceCentered: () => latestCenterStatusRef.current?.isCentered ?? false,
      getCenterStatus: () => latestCenterStatusRef.current,
      getLiveFaceCount: () => faceCount,
      resetCooldown: () => {
        isLockedRef.current = false;
        centeredSinceRef.current = null;
      },
    }),
    [captureFullFrameBlob, faceCount]
  );

  return (
    <div
      className={cn('face-detection', className)}
      style={{
        width,
        height,
        ...style,
      }}
    >
      {/* Video Element */}
      <video
        ref={videoRef}
        playsInline
        muted
        className="face-detection__video"
        style={{
          transform: mirrored ? 'scaleX(-1)' : 'none',
        }}
      />

      {/* Overlay Canvas */}
      <canvas ref={canvasRef} className="face-detection__canvas" />

      {/* Camera Flash Snapshot Effect */}
      {isFlashing && <div className="face-detection__flash" />}

      {/* Loading state */}
      {isLoading && (
        <div className="face-detection__loading">
          <Loader2 className="face-detection__loading-icon" />
          <span className="face-detection__loading-text">Loading MediaPipe BlazeFace...</span>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="face-detection__error">
          <AlertCircle className="face-detection__error-icon" />
          <span>{error}</span>
        </div>
      )}

      {/* Guidance Banner (Center instruction / hold still / progress) */}
      {!isLoading && !error && (
        <div
          className={cn(
            'face-detection__guide-banner',
            isCenteredState ? 'face-detection__guide-banner--centered' : ''
          )}
        >
          <span
            className={cn(
              'face-detection__status-dot',
              isCenteredState
                ? 'face-detection__status-dot--active'
                : faceCount > 0
                  ? 'face-detection__status-dot--aligning'
                  : 'face-detection__status-dot--waiting'
            )}
          />
          <span className="face-detection__guide-text">{guidanceMessage}</span>
        </div>
      )}

      {/* Status indicator badge (Bottom-left) */}
      {!isLoading && !error && (
        <div className="face-detection__status">
          <Camera className="face-detection__status-icon" />
          <span>{faceCount > 0 ? `${faceCount} Face${faceCount > 1 ? 's' : ''}` : 'No Face'}</span>
        </div>
      )}
    </div>
  );
});

export default FaceDetection;