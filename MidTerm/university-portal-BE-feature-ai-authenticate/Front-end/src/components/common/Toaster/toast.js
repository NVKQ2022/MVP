let toasts = [];
let listeners = [];

const notify = () => {
  listeners.forEach((listener) => listener(toasts));
};

const dismiss = (id) => {
  toasts = toasts.filter((t) => t.id !== id);
  notify();
};

const addToast = (type, title, options = {}) => {
  const id = options.id ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const duration = options.duration ?? 4000;

  toasts = [...toasts, { id, type, title, description: options.description }];
  notify();

  if (duration !== Infinity) {
    setTimeout(() => dismiss(id), duration);
  }

  return id;
};

export const toast = {
  success: (title, options) => addToast('success', title, options),
  error: (title, options) => addToast('error', title, options),
  warning: (title, options) => addToast('warning', title, options),
  info: (title, options) => addToast('info', title, options),
  message: (title, options) => addToast('default', title, options),
  dismiss,
};

export const subscribeToasts = (listener) => {
  listeners.push(listener);
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
};

export const getToastsSnapshot = () => toasts;