export function isProblemDetails(error) {
  return !!error?.response?.data?.title;
}

export function getProblemTitle(error) {
  return error?.response?.data?.title;
}

export function getProblemDetail(error) {
  return error?.response?.data?.detail || 'Something went wrong. Please try again.';
}

export function isEmailNotVerifiedError(error) {
  return error?.response?.status === 403 && getProblemTitle(error) === 'Email is not verified';
}
