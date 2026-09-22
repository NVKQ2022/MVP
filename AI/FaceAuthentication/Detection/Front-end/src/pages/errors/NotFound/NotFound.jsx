import { Link } from 'react-router-dom';
import { ArrowLeft, Home } from 'lucide-react';

import { Button } from '@/components/ui/button/button';

const NotFound = () => {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-6">
      <div className="flex max-w-md flex-col items-center text-center">
        <p className="text-7xl font-bold tracking-tight text-primary">404</p>

        <h1 className="mt-6 text-2xl font-semibold tracking-tight">Page not found</h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Sorry, we couldn't find the page you're looking for. The page may have been moved or the
          URL may be incorrect.
        </p>

        <div className="mt-8 flex items-center gap-3">
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              Go to home
            </Link>
          </Button>

          <Button variant="outline" onClick={() => window.history.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go back
          </Button>
        </div>
      </div>
    </main>
  );
};

export default NotFound;
