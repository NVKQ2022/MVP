import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { AppProvider } from '@/providers/AppProvider';
import App from './App.jsx';
import '@/styles/app.scss';
import '@/styles/globals.scss';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProvider>
      <App />
    </AppProvider>
  </StrictMode>,
);
