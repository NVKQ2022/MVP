import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import styles from './ErrorState.module.scss';

export function ErrorState({
  title = 'Something went wrong',
  description = 'Please try again.',
  onRetry,
}) {
  return (
    <div className={styles.errorState}>
      <AlertTriangle size={40} className={styles.errorState__icon} />
      <p className={styles.errorState__title}>{title}</p>
      <p className={styles.errorState__description}>{description}</p>
      {onRetry && (
        <Button variant="outline" size="sm" className={styles.errorState__retry} onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
