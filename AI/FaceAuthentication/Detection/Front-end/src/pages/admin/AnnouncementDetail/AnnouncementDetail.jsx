import { useRef } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import AnnouncementForm from './AnnouncementForm';
import { announcementsData } from '@/data/announcementsData';
import { Button } from '@/components/ui/button/button';
import { Upload } from 'lucide-react';

const AdminAnnouncementDetail = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const announcement = id
    ? (location.state?.announcement ?? announcementsData.find((a) => a.id === id))
    : undefined;

  const isEditMode = Boolean(announcement);

  const handleSubmit = (values) => {
    if (isEditMode) {
      console.log('update announcement', values);
      // TODO: call your update API here, e.g. updateAnnouncement(values.id, values)
    } else {
      console.log('create announcement', values);
      // TODO: call your create API here, e.g. createAnnouncement(values)
    }
    navigate('/announcements');
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

  if (id && !announcement) {
    return <p className="announcement-detail__not-found">Announcement not found.</p>;
  }

  return (
    <div className="announcement-detail">
      <div className="announcement-detail__header">
        <h1 className="announcement-detail__title">
          {isEditMode ? 'Update Announcement' : 'Create Announcement'}
        </h1>

        {!isEditMode && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              className="announcement-detail__file-input"
              onChange={handleFileChange}
            />
            <Button variant="outline" size="sm" onClick={handleImportClick}>
              <Upload className="announcement-detail__btn-icon" />
              Import from file
            </Button>
          </>
        )}
      </div>

      <AnnouncementForm
        announcement={announcement}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
    </div>
  );
};

export default AdminAnnouncementDetail;
