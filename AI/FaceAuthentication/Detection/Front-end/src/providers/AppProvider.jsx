import { TooltipProvider } from '@/components/ui/tooltip/tooltip';
import { ThemeProvider } from '@/providers/ThemeProvider';
import { QueryProvider } from '@/providers/QueryProvider';

export function AppProvider({ children }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        <TooltipProvider>{children}</TooltipProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}
