import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button/button';
import { cn } from '@/utils/cn';
import styles from './NotificationBell.module.scss';

export function NotificationBell({ count = 0 }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Notifications"
      className={styles.notificationBell}
    >
      <Bell size={16} />
      {count > 0 && <span className={cn(styles.notificationBell__dot)} />}
    </Button>
  );
}
