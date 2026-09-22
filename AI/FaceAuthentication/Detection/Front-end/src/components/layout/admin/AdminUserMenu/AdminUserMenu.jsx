import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu/dropdown-menu';
import { UserAvatar } from '@/components/layout/shared/UserAvatar';

export function AdminUserMenu({ onLogout }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button aria-label="Admin user menu">
          <UserAvatar name="Admin User" />
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
