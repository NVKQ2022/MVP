import { Link } from 'react-router-dom';
import { ArrowLeft, Home } from 'lucide-react';

import { Button } from '@/components/ui/button/button';
import styles from './NotFound.module.scss';

const NotFound = () => {
  return (
    <main className={styles.notFound}>
      <div className={styles.notFound__content}>
        <p className={styles.notFound__code}>404</p>

        <h1 className={styles.notFound__title}>Page not found</h1>

        <p className={styles.notFound__description}>
          Sorry, we couldn't find the page you're looking for. The page may have been moved or the
          URL may be incorrect.
        </p>

        <div className={styles.notFound__actions}>
          <Button asChild>
            <Link to="/">
              <Home className={styles.notFound__icon} />
              Go to home
            </Link>
          </Button>

          <Button variant="outline" onClick={() => window.history.back()}>
            <ArrowLeft className={styles.notFound__icon} />
            Go back
          </Button>
        </div>
      </div>
    </main>
  );
};

export default NotFound;