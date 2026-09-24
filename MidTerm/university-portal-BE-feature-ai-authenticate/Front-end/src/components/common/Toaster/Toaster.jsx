import { useSyncExternalStore } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { toast, subscribeToasts, getToastsSnapshot } from './toast';
import styles from './Toaster.module.scss';

const ICONS = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
  default: null,
};

export function Toaster() {
  const toasts = useSyncExternalStore(subscribeToasts, getToastsSnapshot, getToastsSnapshot);

  if (toasts.length === 0) return null;

  return (
    <div className={styles.toaster} role="region" aria-live="polite">
      {toasts.map((t) => {
        const Icon = ICONS[t.type];
        return (
          <div key={t.id} className={`${styles.toast} ${styles[`toast--${t.type}`] ?? ''}`}>
            {Icon && <Icon className={styles.toast__icon} size={18} />}
            <div className={styles.toast__content}>
              <p className={styles.toast__title}>{t.title}</p>
              {t.description && <p className={styles.toast__description}>{t.description}</p>}
            </div>
            <button
              type="button"
              className={styles.toast__close}
              aria-label="Dismiss notification"
              onClick={() => toast.dismiss(t.id)}
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}