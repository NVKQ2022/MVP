import { useMutation, useQueryClient } from '@tanstack/react-query';
import { profileApi } from '../services/profile.api';

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: profileApi.updateMe,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(['profile', 'me'], updatedUser);
    },
  });
}
