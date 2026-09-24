import { TooltipProvider } from '@/components/ui/tooltip/tooltip';
import { ThemeProvider } from '@/providers/ThemeProvider';
import { QueryProvider } from '@/providers/QueryProvider';
import { AuthInitializer } from '@/features/auth';
import { Toaster } from '@/components/common/Toaster';

export function AppProvider({ children }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        <AuthInitializer>
          <TooltipProvider>
            {children}
            <Toaster />
          </TooltipProvider>
        </AuthInitializer>
      </QueryProvider>
    </ThemeProvider>
  );
}
