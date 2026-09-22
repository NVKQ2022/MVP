import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, ShieldCheck, Megaphone, ScrollText } from 'lucide-react';
import { Logo } from '@/components/layout/shared/Logo';
import { cn } from '@/utils/cn';
import styles from './AdminSidebar.module.scss';

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard, end: true },
  { label: 'Users', to: '/users', icon: Users },
  { label: 'Whitelist', to: '/whitelist', icon: ShieldCheck },
  { label: 'Announcements', to: '/announcements', icon: Megaphone },
  { label: 'Audit Logs', to: '/audit-logs', icon: ScrollText },
];

export function AdminSidebar({ className = '', collapsed = false }) {
  return (
    <aside className={cn(styles.sidebar, collapsed && styles['sidebar--collapsed'], className)}>
      <div className={styles.sidebar__header}>
        {collapsed ? <span className={styles.sidebar__mark}>E</span> : <Logo />}
      </div>

      <nav className={styles.sidebar__nav}>
        {navItems.map(({ label, to, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              cn(
                styles.navItem,
                collapsed && styles['navItem--collapsed'],
                isActive && styles['navItem--active'],
              )
            }
          >
            <Icon size={16} className={styles.navItem__icon} />
            {!collapsed && label}
          </NavLink>
        ))}
      </nav>

      {!collapsed && <div className={styles.sidebar__footer}>Admin Console v1.0</div>}
    </aside>
  );
}
