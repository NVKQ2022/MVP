import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar/avatar';
import { Separator } from '@/components/ui/separator/separator';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import { StatusBadge } from '@/components/common/StatusBadge';
import {
  useAdminUserQuery,
  useAdminUserDelete,
  useAdminUserUpdate,
  useAdminUserActivate,
  useAdminUserUnlock,
  useAdminUserLock
} from '@/features/AdminUsers';
import { formatDate } from '@/utils/formatDate';
import { Button } from '@/components/ui/button/button';
import styles from './AdminUserDetail.module.scss';
import { ArrowLeft } from 'lucide-react';
import { InfoRow } from '@/components/ui/inforow/inforow';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

const ROLES = [
  { id: '11111111-1111-1111-1111-111111111111', name: 'Admin' },
  { id: '22222222-2222-2222-2222-222222222222', name: 'Student' },
];

export default function AdminUserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: user, isLoading, isError, refetch } = useAdminUserQuery(id);
  const adminUserDelete = useAdminUserDelete();
  const adminUserUpdate = useAdminUserUpdate();
  const adminUserLock = useAdminUserLock();
  const adminUserUnlock = useAdminUserUnlock();
  const adminUserActivate = useAdminUserActivate();

  const [selectedRoleId, setSelectedRoleId] = useState('');

  const handleDelete = () => {
    adminUserDelete.mutate(id, {
      onSuccess: () => {
        navigate(-1);
      },
      onError: () => {
        alert(`Failed to delete ${user.userName}`);
      },
    });
  };

  const handleUpdate = () => {
    adminUserUpdate.mutate({
      id: user.id,
      roleId: selectedRoleId,
    }, {
      onSuccess: () => {
        setSelectedRoleId('');
      },
      onError: () => {
        alert(`Failed to update role for ${user.userName}`);
      },
    });
  };


  const handleLock = () => {
    adminUserLock.mutate(user.id, {
      onError: () => alert(`Failed to lock ${user.userName}`),
    });
  };

  const handleUnlock = () => {
    adminUserUnlock.mutate(user.id, {
      onError: () => alert(`Failed to unlock ${user.userName}`),
    });
  };

  const handleActivate = () => {
    adminUserActivate.mutate(user.id, {
      onError: () => alert(`Failed to activate ${user.userName}`),
    });
  };

  if (isLoading) return <LoadingState rows={6} />;

  if (isError) {
    return (
      <>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(-1)}
          className={styles.backButton}
        >
          <ArrowLeft size={16} />
          Back
        </Button>
        <ErrorState
          title="Failed to load user"
          description="Something went wrong while fetching this account."
          onRetry={refetch}
        />
      </>
    );
  }

  if (!user) {
    return <EmptyState title="User not found" description="This account may have been deleted." />;
  }

  const initial = (user.userName || user.email || '?').charAt(0).toUpperCase();
  const activeStatus = user.isActive ? 'active' : 'inactive';
  const accountStatus = user.status === 'Normal' ? 'Normal' : 'Locked';
  const isDeleting = adminUserDelete.isPending;
  const isUpdating = adminUserUpdate.isPending;

  return (
    <div className={styles.userDetail}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => navigate(-1)}
        className={styles.backButton}
      >
        <ArrowLeft size={16} />
        Back
      </Button>

      <PageHeader title="User Details" description="Account information" />

      <Card className={styles.summaryCard}>
        <CardContent className={styles.summaryCard__content}>
          <Avatar className={styles.summaryCard__avatar}>
            <AvatarImage src={user.avatarUrl} alt={user.userName} />
            <AvatarFallback>{initial}</AvatarFallback>
          </Avatar>
          <div className={styles.summaryCard__identity}>
            <h2 className={styles.summaryCard__name}>{user.userName || 'Unnamed user'}</h2>
            <p className={styles.summaryCard__email}>{user.email}</p>
          </div>
          <div className={styles.summaryCard__badges}>
            <StatusBadge status={activeStatus} />
            <StatusBadge status={accountStatus} />
          </div>
        </CardContent>
      </Card>

      <div className={styles.userDetail__sections}>
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Contact and personal details</CardDescription>
          </CardHeader>
          <CardContent className={styles.sectionGrid}>
            <InfoRow label="Full Name" value={user.userName} />
            <Separator />
            <InfoRow label="Email" value={user.email} />
            <Separator />
            <InfoRow label="Phone Number" value={user.phoneNumber} />
            <Separator />
            <InfoRow
              label="Date of Birth"
              value={user.dateOfBirth ? formatDate(user.dateOfBirth) : null}
            />
            <Separator />
            <InfoRow label="Gender" value={user.gender} />
            <Separator />
            <InfoRow label="Address" value={user.address} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Role, status, and activity</CardDescription>
          </CardHeader>
          <CardContent className={styles.sectionGrid}>
            <InfoRow label="User ID" value={user.id} truncate />
            <Separator />
            <InfoRow label="Role" value={user.roleName} />
            <Separator />
            <InfoRow
              label="Last Login"
              value={user.lastLoginAt ? formatDate(user.lastLoginAt, { includeTime: true }) : null}
            />
            <Separator />
            <InfoRow label="Member Since" value={formatDate(user.createdAt)} />
            <Separator />
            <InfoRow
              label="Last Updated"
              value={formatDate(user.updatedAt, { includeTime: true })}
            />
          </CardContent>
        </Card>

        <Card className={styles.userDetail__sectionFull}>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
            <CardDescription>Manage this user account</CardDescription>
          </CardHeader>
          <CardContent className={styles.sectionGrid}>
            <div className={styles.actionsGrid}>
              <Select
                value={selectedRoleId}
                onValueChange={setSelectedRoleId}
              >
                <SelectTrigger>
                  <SelectValue placeholder={`Current: ${user.roleName}`} />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((role) => (
                    <SelectItem key={role.id} value={role.id}>
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button
                size="lg"
                variant="outline"
                disabled={isUpdating || isDeleting || !selectedRoleId}
                onClick={handleUpdate}
              >
                {isUpdating ? 'Saving...' : 'Update Role'}
              </Button>

              <Button
                size="lg"
                variant="outline"
                disabled={adminUserLock.isPending || adminUserUnlock.isPending}
                onClick={user.status === 'Normal' ? handleLock : handleUnlock}
                className={styles.actionsGrid__actionButton}
              >
                {adminUserLock.isPending || adminUserUnlock.isPending
                  ? 'Saving...'
                  : user.status === 'Normal' ? 'Lock' : 'Unlock'}
              </Button>

              <Button
                size="lg"
                variant="outline"
                disabled={adminUserActivate.isPending || !user.isActive === false}
                onClick={handleActivate}
                className={styles.actionsGrid__actionButton}
              >
                {adminUserActivate.isPending ? 'Saving...' : 'Activate'}
              </Button>

              <Button
                size="lg"
                variant="destructive"
                disabled={isDeleting || isUpdating}
                onClick={handleDelete}
                className={styles.actionsGrid__actionButton}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}