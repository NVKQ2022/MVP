import { useQuery } from '@tanstack/react-query';
import { profileApi } from '../services/profile.api';

export function useProfile({ enabled = true } = {}) {
  return useQuery({
    queryKey: ['profile', 'me'],
    queryFn: profileApi.getMe,
    enabled,
  });
}
