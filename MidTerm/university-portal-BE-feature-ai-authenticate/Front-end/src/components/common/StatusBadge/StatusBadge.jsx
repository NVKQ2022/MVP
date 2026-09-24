import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';
import styles from './StatusBadge.module.scss';

const statusClassMap = {
  active: styles['status--active'],
  published: styles['status--active'],
  inactive: styles['status--inactive'],
  archived: styles['status--inactive'],
  locked: styles['status--locked'],
  pending: styles['status--pending'],
};

const statusLabels = {
  active: 'Active',
  inactive: 'Inactive',
  locked: 'Locked',
  pending: 'Pending',
  published: 'Published',
  archived: 'Archived',
};

export function StatusBadge({ status, className }) {
  return (
    <Badge
      variant="outline"
      className={cn(statusClassMap[status] || statusClassMap.inactive, className)}
    >
      {statusLabels[status] || status}
    </Badge>
  );
}
