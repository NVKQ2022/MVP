import { env } from '@/config/env';

/**
 * Detects which application surface should render based on hostname.
 * Returns: "student" | "admin" | "unknown"
 */
export function getAppDomain() {
  const hostname = window.location.hostname;

  if (hostname === env.adminHost) {
    return 'admin';
  }

  // 127.0.0.1 is intentionally supported as an alias for the student host
  // during local development (documented in README).
  if (hostname === env.studentHost || hostname === '127.0.0.1') {
    return 'student';
  }

  return 'unknown';
}
