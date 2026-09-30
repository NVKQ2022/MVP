export const appConfig = {
  appName: 'EduPortal',
  defaultPageSize: 10,
  tokenStorageKey: 'auth_access_token',
  refreshTokenStorageKey: 'auth_refresh_token',
  themeStorageKey: 'app_theme',
  authStorageKey: 'auth_user',

  /**
   * Face Authentication & Detection Settings
   * ==========================================
   * Configure wait times and thresholds here.
   */
  faceAuth: {
    /**
     * Wait time (in milliseconds) the face must remain inside the box before automatically sending the request.
     * Default: 800ms (0.8s).
     * Adjust this value: e.g., 500 (fast), 800 (balanced), 1200 (extra stability).
     */
    centerHoldDurationMs: 800,

    /**
     * Cooldown (in milliseconds) between capture attempts.
     */
    cooldownMs: 2500,

    /**
     * Minimum confidence threshold for MediaPipe face detector (0.0 - 1.0).
     */
    minDetectionConfidence: 0.5,
  },
};
