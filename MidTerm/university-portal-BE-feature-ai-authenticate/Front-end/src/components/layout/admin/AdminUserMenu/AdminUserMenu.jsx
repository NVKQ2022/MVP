import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { UserAvatar } from '@/components/layout/shared/UserAvatar';
import apiClient from '@/services/api';
import { useQuery } from '@tanstack/react-query';

export function AdminUserMenu({ onLogout }) {
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/users/me');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const displayName = profile?.userName ?? 'Admin User';
  const email = profile?.email;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button aria-label="Admin user menu">
          <UserAvatar name={displayName} />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Settings</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onLogout}>Logout</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
