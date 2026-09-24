export function formatDate(isoString, { includeTime = false } = {}) {
  if (!isoString) return '—';

  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return '—';

  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...(includeTime && { hour: '2-digit', minute: '2-digit' }),
  });
}

// For <input type="date"> which needs strict yyyy-MM-dd, not a locale string.
export function toDateInputValue(isoString) {
  if (!isoString) return '';
  return isoString.split('T')[0];
}
