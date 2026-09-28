import { useNavigate, useParams } from 'react-router-dom';
import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import { ErrorState } from '@/components/common/ErrorState';
import { useAuditLogQuery } from '@/features/AuditLogs';

const ACTION_BADGE_VARIANT = {
  EntityCreated: 'default',
  EntityUpdated: 'secondary',
  EntityDeleted: 'destructive',
};

function formatTimestamp(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('en-US', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function formatJsonValue(value) {
  if (!value) return null;
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}

function DetailField({ label, value, mono = false }) {
  return (
    <div className="audit-log-detail__field">
      <span className="audit-log-detail__field-label">{label}</span>
      <span className={mono ? 'audit-log-detail__field-value audit-log-detail__field-value--mono' : 'audit-log-detail__field-value'}>
        {value || '-'}
      </span>
    </div>
  );
}

const AuditLogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: log, isLoading, isError, refetch } = useAuditLogQuery(id);

  const handleBack = () => navigate('/audit-logs');

  if (isError) {
    return (
      <div className="audit-log-detail">
        <Button variant="outline" className="audit-log-detail__back-button" onClick={handleBack}>
          ← Back to Audit Logs
        </Button>
        <ErrorState
          title="Failed to load audit log"
          description="We couldn't load this audit log. Please try again."
          onRetry={refetch}
        />
      </div>
    );
  }

  if (isLoading || !log) {
    return (
      <div className="audit-log-detail">
        <p className="audit-log-detail__loading">Loading...</p>
        <Button variant="outline" className="audit-log-detail__back-button" onClick={handleBack}>
          ← Back to Audit Logs
        </Button>
      </div>
    );
  }

  const oldValues = formatJsonValue(log.oldValues);
  const newValues = formatJsonValue(log.newValues);

  return (
    <div className="audit-log-detail">
      <div className="audit-log-detail__header audit-log-detail__header--inline">
        <div className="audit-log-detail__title-row">
          <h1 className="audit-log-detail__title">Audit Log Detail</h1>
          <Badge variant={ACTION_BADGE_VARIANT[log.action] ?? 'outline'}>{log.action}</Badge>
        </div>
        <Button variant="outline" onClick={handleBack}>
          ← Back to Audit Logs
        </Button>
      </div>

      <section className="audit-log-detail__section">
        <h2 className="audit-log-detail__section-title">Overview</h2>
        <div className="audit-log-detail__grid">
          <DetailField label="Timestamp" value={formatTimestamp(log.createdAt)} />
          <DetailField label="Log ID" value={log.id} mono />
          <DetailField label="Trace ID" value={log.traceId} mono />
        </div>
      </section>

      <section className="audit-log-detail__section">
        <h2 className="audit-log-detail__section-title">User</h2>
        <div className="audit-log-detail__grid">
          <DetailField label="Name" value={log.userName} />
          <DetailField label="Email" value={log.userEmail} />
          <DetailField label="User ID" value={log.userId} mono />
          <DetailField label="IP Address" value={log.ipAddress} mono />
          <DetailField label="User Agent" value={log.userAgent} />
        </div>
      </section>

      <section className="audit-log-detail__section">
        <h2 className="audit-log-detail__section-title">Entity</h2>
        <div className="audit-log-detail__grid">
          <DetailField label="Entity Type" value={log.entityType} />
          <DetailField label="Entity ID" value={log.entityId} mono />
          <DetailField label="Request Path" value={log.requestPath} mono />
        </div>
      </section>

      {(oldValues || newValues) && (
        <section className="audit-log-detail__section">
          <h2 className="audit-log-detail__section-title">Changes</h2>
          <div className="audit-log-detail__diff-grid">
            <div className="audit-log-detail__diff-column">
              <span className="audit-log-detail__field-label">Old Values</span>
              <pre className="audit-log-detail__code-block">{oldValues || '—'}</pre>
            </div>
            <div className="audit-log-detail__diff-column">
              <span className="audit-log-detail__field-label">New Values</span>
              <pre className="audit-log-detail__code-block">{newValues || '—'}</pre>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default AuditLogDetail;