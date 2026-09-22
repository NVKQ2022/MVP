import { useEffect, useRef, useState, useCallback } from 'react';
import { FilesetResolver, FaceDetector } from '@mediapipe/tasks-vision';
import { Camera, AlertCircle, Loader2 } from 'lucide-react';

export function FaceDetection({
  onFaceDetected,
  minConfidence = 0.5,
  mirrored = true,
  showOverlay = true,
  themeColor = '#0284c7',
  width = '100%',
  height = 360,
  className = '',
  style = {},
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectorRef = useRef(null);
  const requestRef = useRef(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faceCount, setFaceCount] = useState(0);

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

        setFaceCount(detections.length);
        if (onFaceDetected) {
          onFaceDetected(detections);
        }

        if (showOverlay && detections.length > 0) {
          detections.forEach((detection) => {
            const { originX, originY, width: boxWidth, height: boxHeight } = detection.boundingBox;
            const score = detection.categories?.[0]?.score ?? 0;

            const x = mirrored ? canvas.width - originX - boxWidth : originX;

            // Draw bounding box
            ctx.save();
            ctx.strokeStyle = themeColor;
            ctx.lineWidth = 3;
            ctx.shadowColor = themeColor;
            ctx.shadowBlur = 10;
            ctx.strokeRect(x, originY, boxWidth, boxHeight);

            // Draw score pill
            const label = `Face: ${(score * 100).toFixed(0)}%`;
            ctx.font = 'bold 13px sans-serif';
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
            ctx.fillRect(x, Math.max(0, originY - 24), textWidth + 14, 22);
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, x + 7, Math.max(16, originY - 8));

            // Draw 6 BlazeFace Keypoints
            if (detection.keypoints) {
              detection.keypoints.forEach((kp) => {
                const kx = mirrored ? canvas.width - kp.x * canvas.width : kp.x * canvas.width;
                const ky = kp.y * canvas.height;

                ctx.beginPath();
                ctx.arc(kx, ky, 4, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = themeColor;
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
  }, [mirrored, showOverlay, themeColor, onFaceDetected]);

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

  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-slate-950 flex items-center justify-center ${className}`}
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
        className="w-full h-full object-cover"
        style={{
          transform: mirrored ? 'scaleX(-1)' : 'none',
        }}
      />

      {/* Overlay Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none object-cover"
      />

      {/* Loading state */}
      {isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 text-white gap-3 p-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <span className="text-sm font-medium">Loading MediaPipe BlazeFace...</span>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-red-950/90 text-red-200 p-4 text-center gap-2">
          <AlertCircle className="w-8 h-8 text-red-400" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Status indicator badge */}
      {!isLoading && !error && (
        <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-md text-white text-xs font-medium px-3 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
          <span
            className={`w-2 h-2 rounded-full ${faceCount > 0 ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`}
          />
          <Camera className="w-3.5 h-3.5 opacity-70" />
          <span>{faceCount > 0 ? `${faceCount} Face${faceCount > 1 ? 's' : ''} Detected` : 'Looking for face...'}</span>
        </div>
      )}
    </div>
  );
}

export default FaceDetection;
