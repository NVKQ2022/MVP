export function redirectToHostWithSession(host, { accessToken, refreshToken }) {
  const port = window.location.port ? `:${window.location.port}` : '';
  const params = new URLSearchParams({ at: accessToken, rt: refreshToken ?? '' });
  window.location.assign(`http://${host}${port}/auth/callback?${params.toString()}`);
}
