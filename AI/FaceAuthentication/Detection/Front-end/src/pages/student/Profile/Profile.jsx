import { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card/card';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Badge } from '@/components/ui/badge/badge';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import { UserAvatar } from '@/components/layout/shared/UserAvatar';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { useProfile, useUpdateProfile } from '@/features/users';
import { formatDate, toDateInputValue } from '@/utils/formatDate';
import styles from './Profile.module.scss';

const GENDER_OPTIONS = ['Male', 'Female', 'Other'];

export default function StudentProfile() {
  const { data: profile, isLoading, isError, refetch } = useProfile();
  const updateProfile = useUpdateProfile();

  const [form, setForm] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (profile) setForm(profile);
  }, [profile]);

  if (isLoading || !form) return <LoadingState rows={4} />;
  if (isError) return <ErrorState onRetry={refetch} />;

  const handleChange = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleGenderChange = (value) => setForm((prev) => ({ ...prev, gender: value }));

  const handleCancel = () => {
    setForm(profile);
    setIsEditing(false);
  };

  const handleSave = (e) => {
    e.preventDefault();
    updateProfile.mutate(
      {
        userName: form.userName,
        phoneNumber: form.phoneNumber,
        address: form.address,
        gender: form.gender,
        dateOfBirth: form.dateOfBirth,
      },
      { onSuccess: () => setIsEditing(false) },
    );
  };

  return (
    <div className={styles.profile}>
      <PageHeader title="Profile" description="Your personal account information" />

      <Card>
        <CardHeader className={styles.profile__header}>
          {/* <UserAvatar
            name={form.userName}
            imageUrl={form.avatarUrl}
            className={styles.profile__avatar}
          /> */}
          <div>
            <CardTitle>{form.userName}</CardTitle>
            <CardDescription>{form.email}</CardDescription>
          </div>
          <div className={styles.profile__badges}>
            <Badge variant="secondary">{form.role}</Badge>
            <Badge variant={form.isActive ? 'default' : 'outline'}>
              {form.isActive ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </CardHeader>

        <form onSubmit={handleSave}>
          <CardContent className={styles.profile__grid}>
            {updateProfile.isError && (
              <Alert variant="destructive" className={styles.profile__alert}>
                <AlertDescription>Failed to update profile. Please try again.</AlertDescription>
              </Alert>
            )}

            <div className={styles.field}>
              <Label htmlFor="userName">Full Name</Label>
              <Input
                id="userName"
                value={form.userName || ''}
                onChange={handleChange('userName')}
                disabled={!isEditing}
              />
            </div>

            <div className={styles.field}>
              <Label>Email</Label>
              <p className={styles.field__readOnly}>{form.email}</p>
            </div>

            <div className={styles.field}>
              <Label htmlFor="phoneNumber">Phone Number</Label>
              <Input
                id="phoneNumber"
                value={form.phoneNumber || ''}
                onChange={handleChange('phoneNumber')}
                disabled={!isEditing}
              />
            </div>

            <div className={styles.field}>
              <Label htmlFor="dateOfBirth">Date of Birth</Label>
              <Input
                id="dateOfBirth"
                type="date"
                value={toDateInputValue(form.dateOfBirth)}
                onChange={handleChange('dateOfBirth')}
                disabled={!isEditing}
              />
            </div>

            <div className={styles.field}>
              <Label htmlFor="gender">Gender</Label>
              <Select value={form.gender} onValueChange={handleGenderChange} disabled={!isEditing}>
                <SelectTrigger id="gender">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  {GENDER_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className={cn_field(styles)}>
              <Label htmlFor="address">Address</Label>
              <Input
                id="address"
                value={form.address || ''}
                onChange={handleChange('address')}
                disabled={!isEditing}
              />
            </div>

            <div className={styles.field}>
              <Label>Last Login</Label>
              <p className={styles.field__readOnly}>
                {formatDate(form.lastLoginAt, { includeTime: true })}
              </p>
            </div>

            <div className={styles.field}>
              <Label>Member Since</Label>
              <p className={styles.field__readOnly}>{formatDate(form.createdAt)}</p>
            </div>
          </CardContent>

          <CardFooter className={styles.profile__footer}>
            {!isEditing ? (
              <Button type="button" onClick={() => setIsEditing(true)}>
                Edit Profile
              </Button>
            ) : (
              <>
                <Button type="submit" disabled={updateProfile.isPending}>
                  {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </>
            )}
            {updateProfile.isSuccess && !isEditing && (
              <span className={styles.profile__savedNote}>Saved</span>
            )}
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

function cn_field(styles) {
  return `${styles.field} ${styles['field--full']}`;
}
