import { Moon, Sun, Monitor } from 'lucide-react';
import { Button } from '@/components/ui/button/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { useTheme } from '@/providers/ThemeProvider';
import styles from './ThemeToggle.module.scss';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle theme"
          className={styles.themeToggle}
        >
          <Sun size={16} className={styles.themeToggle__sun} />
          <Moon size={16} className={styles.themeToggle__moon} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme('light')} className={styles.themeToggle__item}>
          <Sun size={16} />
          Light
          {theme === 'light' && <span className={styles.themeToggle__check}>✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')} className={styles.themeToggle__item}>
          <Moon size={16} />
          Dark
          {theme === 'dark' && <span className={styles.themeToggle__check}>✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')} className={styles.themeToggle__item}>
          <Monitor size={16} />
          System
          {theme === 'system' && <span className={styles.themeToggle__check}>✓</span>}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
