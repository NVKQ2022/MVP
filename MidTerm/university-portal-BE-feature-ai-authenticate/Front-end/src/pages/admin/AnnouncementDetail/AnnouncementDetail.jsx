import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Pencil, CalendarDays, User } from 'lucide-react';
import { Button } from '@/components/ui/button/button';
import { Badge } from '@/components/ui/badge/badge';
import { Separator } from '@/components/ui/separator/separator';
import { Skeleton } from '@/components/ui/skeleton/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area/scroll-area';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card/card';
import { ErrorState } from '@/components/common/ErrorState';
import { useAnnouncementQuery } from '@/features/AdminAnnouncement';

// Đồng bộ với STATUS_LABEL trong Announcements.jsx (list page).
// TODO: nên tách map này ra 1 file constants dùng chung, vd.
// '@/features/AdminAnnouncement/constants.js', để tránh lệch nhau giữa 2 trang.
const STATUS_LABEL = {
  Published: { label: 'Published', variant: 'default' },
  Draft: { label: 'Draft', variant: 'outline' },
  Archived: { label: 'Archived', variant: 'secondary' },
};

// TODO: xác nhận danh sách giá trị thật của enum Audience từ BE (vd. All, Student,
// Staff, Teacher...) để map sang label tiếng Việt/đẹp hơn nếu cần. Tạm hiển thị
// nguyên giá trị trả về.
const formatAudience = (audience) => (audience == null ? null : String(audience));

const formatDate = (value) =>
  value
    ? new Date(value).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

const AnnouncementDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, isError, refetch } = useAnnouncementQuery(id);

  const handleBack = () => navigate('/announcements');
  const handleEdit = () => navigate(`/announcements/${id}/edit`);

  if (isError) {
    return (
      <div className="announcement-detail">
        <div className="announcement-detail__toolbar">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="announcement-detail__btn-icon" />
            Back
          </Button>
        </div>
        <ErrorState
          title="Failed to load announcement"
          description="We couldn't load this announcement. Please try again."
          onRetry={refetch}
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="announcement-detail">
        <div className="announcement-detail__toolbar">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="announcement-detail__btn-icon" />
            Back
          </Button>
        </div>
        <Card className="announcement-detail__card">
          <CardHeader>
            <Skeleton className="announcement-detail__skeleton-title" />
            <Skeleton className="announcement-detail__skeleton-meta" />
          </CardHeader>
          <CardContent>
            <Skeleton className="announcement-detail__skeleton-line" />
            <Skeleton className="announcement-detail__skeleton-line" />
            <Skeleton className="announcement-detail__skeleton-line announcement-detail__skeleton-line--short" />
          </CardContent>
        </Card>
      </div>
    );
  }

  const {
    title,
    content,
    audience,
    publicationStatus,
    creatorName,
    publishedAt,
    createdAt,
    updatedAt,
  } = data ?? {};

  const statusInfo = STATUS_LABEL[publicationStatus] ?? {
    label: publicationStatus ?? '-',
    variant: 'default',
  };
  const audienceLabel = formatAudience(audience);

  return (
    <div className="announcement-detail">
      <div className="announcement-detail__toolbar">
        <Button variant="ghost" size="sm" onClick={handleBack}>
          <ArrowLeft className="announcement-detail__btn-icon" />
          Back
        </Button>
        <Button size="sm" onClick={handleEdit}>
          <Pencil className="announcement-detail__btn-icon" />
          Edit
        </Button>
      </div>

      <Card className="announcement-detail__card">
        <CardHeader className="announcement-detail__header">
          <div className="announcement-detail__header-top">
            <CardTitle className="announcement-detail__title">{title}</CardTitle>
            <div className="announcement-detail__badges">
              <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
              {audienceLabel && <Badge variant="outline">{audienceLabel}</Badge>}
            </div>
          </div>

          <div className="announcement-detail__meta">
            {creatorName && (
              <span className="announcement-detail__meta-item">
                <User className="announcement-detail__meta-icon" />
                {creatorName}
              </span>
            )}
            {publishedAt && (
              <span className="announcement-detail__meta-item">
                <CalendarDays className="announcement-detail__meta-icon" />
                Published {formatDate(publishedAt)}
              </span>
            )}
            {!publishedAt && createdAt && (
              <span className="announcement-detail__meta-item">
                <CalendarDays className="announcement-detail__meta-icon" />
                Created {formatDate(createdAt)}
              </span>
            )}
            {updatedAt && (
              <span className="announcement-detail__meta-item announcement-detail__meta-item--muted">
                Last updated {formatDate(updatedAt)}
              </span>
            )}
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="announcement-detail__content">
          <ScrollArea className="announcement-detail__scroll">
            {/* TODO: nếu "content" là rich text/HTML từ WYSIWYG editor, cần sanitize
                (vd. DOMPurify) trước khi dangerouslySetInnerHTML để tránh XSS. */}
            <div
              className="announcement-detail__body"
              dangerouslySetInnerHTML={{ __html: content ?? '' }}
            />
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnnouncementDetail;