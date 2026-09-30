import { useState } from 'react';
import { useNavigate, NavLink, Link } from 'react-router-dom';
import { Menu, Bell } from 'lucide-react';
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
import { useProfile } from '@/features/users';
import { useAuth } from '@/features/auth';
import { useUnreadAnnouncementsQuery } from '@/features/StudentAnnouncement';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Announcements', to: '/announcements' },
  { label: 'Profile', to: '/profile' },
];

export function StudentHeader() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navLinkClass = ({ isActive }) => cn(styles.navLink, isActive && styles['navLink--active']);

  const navigate = useNavigate();

  const { isAuthenticated, status, logout } = useAuth();
  const isCheckingAuth = status === 'idle' || status === 'loading';

  const { data: profile } = useProfile({ enabled: isAuthenticated });

  const { data: unreadData, isLoading: isUnreadLoading } = useUnreadAnnouncementsQuery({
    enabled: isAuthenticated,
  });

  const unreadAnnouncements = unreadData?.items ?? [];
  const unreadCount = unreadData?.totalCount ?? 0;

  const displayName = profile?.userName ?? 'Student User';

  const handleLogout = async () => {
    await logout();
  };

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

          {isCheckingAuth ? null : isAuthenticated && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={styles.header__bellButton} aria-label="Announcements">
                  <Bell size={20} />
                  {unreadCount > 0 && (
                    <span className={styles.header__bellBadge}>
                      {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className={styles.notificationMenu}>
                <div className={styles.notificationMenu__header}>Announcements</div>
                <DropdownMenuSeparator />
                <div className={styles.notificationMenu__list}>
                  {isUnreadLoading ? (
                    <div className={styles.notificationMenu__empty}>Loading...</div>
                  ) : unreadAnnouncements.length === 0 ? (
                    <div className={styles.notificationMenu__empty}>No new announcements</div>
                  ) : (
                    unreadAnnouncements.map((item) => (
                      <DropdownMenuItem key={item.id} asChild>
                        <Link to={`/announcements/${item.id}`} className={styles.notificationMenu__item}>
                          <span className={cn(styles.notificationMenu__itemTitle, 'truncate')}>
                            {item.title}
                          </span>
                          <span className={styles.notificationMenu__itemMeta}>{item.creatorName}</span>
                        </Link>
                      </DropdownMenuItem>
                    ))
                  )}
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          {isCheckingAuth ? null : isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={styles.header__avatarButton} aria-label="User menu">
                  <UserAvatar name={displayName} imageUrl={profile?.avatarUrl} />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link to="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings')}>Settings</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className={styles.header__authActions}>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/login">Sign in</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/signup">Sign up</Link>
              </Button>
            </div>
          )}

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

              {!isCheckingAuth && (
                <div className={styles.mobileAuthActions}>
                  {isAuthenticated ? (
                    <Button
                      variant="outline"
                      onClick={() => {
                        handleLogout();
                        setMobileOpen(false);
                      }}
                    >
                      Logout
                    </Button>
                  ) : (
                    <>
                      <Button variant="outline" asChild onClick={() => setMobileOpen(false)}>
                        <Link to="/login">Sign in</Link>
                      </Button>
                      <Button asChild onClick={() => setMobileOpen(false)}>
                        <Link to="/signup">Sign up</Link>
                      </Button>
                    </>
                  )}
                </div>
              )}
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}