import { Link } from 'react-router-dom';
import { appConfig } from '@/config/appConfig';
import styles from './StudentFooter.module.scss';

export function StudentFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.footer__inner}>
        <p>
          &copy; {year} {appConfig.appName}. All rights reserved.
        </p>
        <nav className={styles.footer__nav}>
          <Link to="/">Home</Link>
          <Link to="/announcements">Announcements</Link>
          <Link to="/profile">Profile</Link>
        </nav>
      </div>
    </footer>
  );
}
