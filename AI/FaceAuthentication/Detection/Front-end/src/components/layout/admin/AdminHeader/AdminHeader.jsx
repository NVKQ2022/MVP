import { useState } from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button/button';
import { Sheet, SheetContent } from '@/components/ui/sheet/sheet';
import { ThemeToggle } from '@/components/layout/shared/ThemeToggle';
import { NotificationBell } from '@/components/layout/shared/NotificationBell';
import { AdminSidebar } from '@/components/layout/admin/AdminSidebar';
import { AdminUserMenu } from '@/components/layout/admin/AdminUserMenu';
import { useAuth } from '@/features/auth';
import { env } from '@/config/env';
import styles from './AdminHeader.module.scss';

export function AdminHeader({ title = 'Dashboard' }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    const port = window.location.port ? `:${window.location.port}` : '';
    window.location.assign(`http://${env.adminHost}${port}/login`);
  };

  return (
    <header className={styles.header}>
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <Button
          variant="ghost"
          size="icon"
          className={styles.header__mobileTrigger}
          aria-label="Open sidebar"
          onClick={() => setMobileOpen(true)}
        >
          <Menu size={20} />
        </Button>
        <SheetContent side="left" className={styles.header__mobileSheet}>
          <AdminSidebar className={styles.header__mobileSidebar} />
        </SheetContent>
      </Sheet>

      <div className={styles.header__title}>
        <h1>{title}</h1>
      </div>

      <div className={styles.header__actions}>
        <ThemeToggle />
        <NotificationBell count={0} />
        <AdminUserMenu onLogout={handleLogout} />
      </div>
    </header>
  );
}
