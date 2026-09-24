import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { cn } from '@/utils/cn';
import styles from './SearchInput.module.scss';

export function SearchInput({ value, onChange, placeholder = 'Search...', className }) {
  return (
    <div className={cn(styles.searchInput, className)}>
      <Search size={16} className={styles.searchInput__icon} />
      <Input
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className={styles.searchInput__field}
      />
    </div>
  );
}
