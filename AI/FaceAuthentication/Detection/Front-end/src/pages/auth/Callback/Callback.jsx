import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { authStore } from '@/features/auth/auth.store';

import './Callback.scss';

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = searchParams.get('at');
    const refreshToken = searchParams.get('rt') || null;

    if (!accessToken) {
      navigate('/login', { replace: true });
      return;
    }

    authStore.setTokens({
      accessToken,
      refreshToken,
    });

    navigate('/', { replace: true });
  }, [searchParams, navigate]);

  return <div className="auth-callback">Signing you in…</div>;
}
