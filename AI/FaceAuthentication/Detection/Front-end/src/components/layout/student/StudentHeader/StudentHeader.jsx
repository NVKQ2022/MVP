import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet/sheet';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { Logo } from '@/components/layout/shared/Logo';
import { ThemeToggle } from '@/components/layout/shared/ThemeToggle';
import { UserAvatar } from '@/components/layout/shared/UserAvatar';
import { cn } from '@/utils/cn';
import styles from './StudentHeader.module.scss';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Announcements', to: '/announcements' },
  { label: 'Profile', to: '/profile' },
];

export function StudentHeader() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinkClass = ({ isActive }) => cn(styles.navLink, isActive && styles['navLink--active']);

  return (
    <header className={styles.header}>
      <div className={styles.header__inner}>
        <Logo />

        <nav className={styles.header__nav}>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} className={navLinkClass}>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className={styles.header__actions}>
          <ThemeToggle />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className={styles.header__avatarButton} aria-label="User menu">
                <UserAvatar name="Student User" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className={styles.header__mobileTrigger}
                aria-label="Open menu"
              >
                <Menu size={20} />
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <SheetHeader>
                <SheetTitle>
                  <Logo />
                </SheetTitle>
              </SheetHeader>
              <nav className={styles.mobileNav}>
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    className={navLinkClass}
                    onClick={() => setMobileOpen(false)}
                  >
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
