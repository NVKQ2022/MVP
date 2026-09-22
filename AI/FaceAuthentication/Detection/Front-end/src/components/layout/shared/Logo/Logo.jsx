import { Link } from 'react-router-dom';
import { GraduationCap } from 'lucide-react';
import { cn } from '@/utils/cn';
import { appConfig } from '@/config/appConfig';
import styles from './Logo.module.scss';

export function Logo({ to = '/', className = '' }) {
  return (
    <Link to={to} className={cn(styles.logo, className)}>
      <GraduationCap size={24} className={styles.logo__icon} />
      <span className={styles.logo__text}>{appConfig.appName}</span>
    </Link>
  );
}
