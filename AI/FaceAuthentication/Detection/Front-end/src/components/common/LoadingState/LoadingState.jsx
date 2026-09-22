import { Skeleton } from '@/components/ui/skeleton/skeleton';
import styles from './LoadingState.module.scss';

export function LoadingState({ rows = 5 }) {
  return (
    <div className={styles.loadingState}>
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className={styles.loadingState__row} />
      ))}
    </div>
  );
}
