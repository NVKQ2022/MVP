import { Inbox } from 'lucide-react';
import styles from './EmptyState.module.scss';

export function EmptyState({ icon: Icon = Inbox, title = 'No data found', description, action }) {
  return (
    <div className={styles.emptyState}>
      <Icon size={40} className={styles.emptyState__icon} />
      <p className={styles.emptyState__title}>{title}</p>
      {description && <p className={styles.emptyState__description}>{description}</p>}
      {action && <div className={styles.emptyState__action}>{action}</div>}
    </div>
  );
}
