import { cn } from '@/utils/cn';
import './skeleton.scss';

function Skeleton({ className, ...props }) {
  return <div className={cn('skeleton', className)} {...props} />;
}

export { Skeleton };
