import { useRef } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import AnnouncementForm from './AnnouncementForm';
import {
  useAnnouncementQuery,
  useCreateAnnouncement,
  useUpdateAnnouncement,
} from '@/features/AdminAnnouncement';
import { Button } from '@/components/ui/button/button';
import { Upload } from 'lucide-react';
import { ErrorState } from '@/components/common/ErrorState';
import { toast } from '@/components/common/Toaster/toast';

const AnnouncementWriteDetail = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const isEditMode = Boolean(id);
  const stateAnnouncement = location.state?.announcement;

  const {
    data: fetchedAnnouncement,
    isLoading,
    isError,
    refetch,
  } = useAnnouncementQuery(!stateAnnouncement ? id : undefined);

  const announcement = stateAnnouncement ?? fetchedAnnouncement;

  const createMutation = useCreateAnnouncement();
  const updateMutation = useUpdateAnnouncement();
  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const handleSubmit = (values) => {
    const mutation = isEditMode
      ? updateMutation.mutateAsync({ id, ...values })
      : createMutation.mutateAsync(values);

    mutation
      .then(() => {
        toast.success(isEditMode ? 'Announcement updated' : 'Announcement created');
        navigate('/announcements');
      })
      .catch((error) => {
        console.error('Failed to save announcement', error);
        toast.error('Failed to save announcement', {
          description: error?.message ?? 'Please try again.',
        });
      });
  };

  const handleCancel = () => navigate('/announcements');

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    console.log('import from file', file);
    // TODO: parse/upload the selected file and populate the form fields

    // reset input so selecting the same file again still fires onChange
    e.target.value = '';
  };

  if (isEditMode && !stateAnnouncement && isLoading) {
    return <p className="announcement-write-detail__loading">Loading...</p>;
  }

  if (isEditMode && !stateAnnouncement && isError) {
    return (
      <ErrorState
        title="Failed to load announcement"
        description="We couldn't load this announcement. Please try again."
        onRetry={refetch}
      />
    );
  }

  return (
    <div className="announcement-write-detail">
      <div className="announcement-write-detail__header">
        <h1 className="announcement-write-detail__title">
          {isEditMode ? 'Update Announcement' : 'Create Announcement'}
        </h1>

        {!isEditMode && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              className="announcement-write-detail__file-input"
              onChange={handleFileChange}
            />
            <Button variant="outline" size="sm" onClick={handleImportClick}>
              <Upload className="announcement-write-detail__btn-icon" />
              Import from file
            </Button>
          </>
        )}
      </div>

      <AnnouncementForm
        announcement={announcement}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        submitting={isSubmitting}
      />
    </div>
  );
};

export default AnnouncementWriteDetail;