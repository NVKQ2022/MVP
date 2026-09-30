import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CalendarDays, User } from 'lucide-react';
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
import { useAnnouncementQuery } from '@/features/StudentAnnouncement';

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

const StudentAnnouncementDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, isError, refetch } = useAnnouncementQuery(id);

  const handleBack = () => navigate('/announcements');

  if (isError) {
    return (
      <div className="student-announcement-detail">
        <div className="student-announcement-detail__toolbar">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="student-announcement-detail__btn-icon" />
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
      <div className="student-announcement-detail">
        <div className="student-announcement-detail__toolbar">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="student-announcement-detail__btn-icon" />
            Back
          </Button>
        </div>
        <Card className="student-announcement-detail__card">
          <CardHeader>
            <Skeleton className="student-announcement-detail__skeleton-title" />
            <Skeleton className="student-announcement-detail__skeleton-meta" />
          </CardHeader>
          <CardContent>
            <Skeleton className="student-announcement-detail__skeleton-line" />
            <Skeleton className="student-announcement-detail__skeleton-line" />
            <Skeleton className="student-announcement-detail__skeleton-line student-announcement-detail__skeleton-line--short" />
          </CardContent>
        </Card>
      </div>
    );
  }

  const { title, content, creatorName, publishedAt, createdAt, isRead } = data ?? {};

  return (
    <div className="student-announcement-detail">
      <div className="student-announcement-detail__toolbar">
        <Button variant="ghost" size="sm" onClick={handleBack}>
          <ArrowLeft className="student-announcement-detail__btn-icon" />
          Back
        </Button>
      </div>

      <Card className="student-announcement-detail__card">
        <CardHeader className="student-announcement-detail__header">
          <div className="student-announcement-detail__header-top">
            <CardTitle className="student-announcement-detail__title">{title}</CardTitle>
          </div>

          <div className="student-announcement-detail__meta">
            {creatorName && (
              <span className="student-announcement-detail__meta-item">
                <User className="student-announcement-detail__meta-icon" />
                {creatorName}
              </span>
            )}
            {publishedAt && (
              <span className="student-announcement-detail__meta-item">
                <CalendarDays className="student-announcement-detail__meta-icon" />
                Published {formatDate(publishedAt)}
              </span>
            )}
            {!publishedAt && createdAt && (
              <span className="student-announcement-detail__meta-item">
                <CalendarDays className="student-announcement-detail__meta-icon" />
                Created {formatDate(createdAt)}
              </span>
            )}
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="student-announcement-detail__content">
          <ScrollArea className="student-announcement-detail__scroll">
            <div
              className="student-announcement-detail__body"
              dangerouslySetInnerHTML={{ __html: content ?? '' }}
            />
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default StudentAnnouncementDetail;