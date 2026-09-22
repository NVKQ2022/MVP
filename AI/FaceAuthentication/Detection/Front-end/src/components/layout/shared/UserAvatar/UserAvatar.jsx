import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar/avatar';

function getInitials(name = '') {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

export function UserAvatar({ name = 'User', imageUrl, className = '' }) {
  return (
    <Avatar className={className}>
      {imageUrl && <AvatarImage src={imageUrl} alt={name} />}
      <AvatarFallback>{getInitials(name)}</AvatarFallback>
    </Avatar>
  );
}
