import { createContext, useContext, useEffect, useState } from 'react';
import { appConfig } from '@/config/appConfig';

const ThemeProviderContext = createContext(undefined);

function getSystemTheme() {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyThemeClass(resolvedTheme) {
  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(resolvedTheme);
}

export function ThemeProvider({ children, defaultTheme = 'system' }) {
  const [theme, setThemeState] = useState(() => {
    const stored = localStorage.getItem(appConfig.themeStorageKey);
    return stored || defaultTheme;
  });

  useEffect(() => {
    const resolvedTheme = theme === 'system' ? getSystemTheme() : theme;
    applyThemeClass(resolvedTheme);

    if (theme !== 'system') return;

    // Keep in sync if the OS theme changes while "system" is selected.
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => applyThemeClass(getSystemTheme());
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const setTheme = (newTheme) => {
    localStorage.setItem(appConfig.themeStorageKey, newTheme);
    setThemeState(newTheme);
  };

  const value = {
    theme,
    setTheme,
    resolvedTheme: theme === 'system' ? getSystemTheme() : theme,
  };

  return <ThemeProviderContext.Provider value={value}>{children}</ThemeProviderContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeProviderContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
