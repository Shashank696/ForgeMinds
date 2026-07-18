import { getRiskColor, getRiskBadgeClass, capitalize, formatDate } from '../../utils/formatters';
import { Clock } from 'lucide-react';

export default function FailureTimeline({ events = [] }) {
  if (!events.length) {
    return (
      <div className="empty-state">
        <Clock size={40} />
        <h3>No events recorded</h3>
        <p>No maintenance or failure events found</p>
      </div>
    );
  }

  return (
    <div className="timeline">
      {events.map((evt, i) => {
        const color = getRiskColor(evt.severity || 'medium');
        return (
          <div key={evt.id || i} className="timeline-item">
            <div className="timeline-dot" style={{ background: color }} />
            <div>
              <p className="text-xs text-muted font-medium">{formatDate(evt.date)}</p>
              <p className="text-sm font-medium" style={{ marginTop: 2 }}>{evt.description}</p>
              <div className="flex gap-sm" style={{ marginTop: 4, flexWrap: 'wrap' }}>
                {evt.severity && <span className={`badge ${getRiskBadgeClass(evt.severity)}`}>{capitalize(evt.severity)}</span>}
                {evt.type && <span className="badge badge-secondary">{capitalize(evt.type)}</span>}
                {evt.technician && <span className="text-xs text-muted">By {evt.technician}</span>}
              </div>
              {evt.root_cause && <p className="text-xs text-secondary" style={{ marginTop: 4 }}>Root Cause: {evt.root_cause}</p>}
              {evt.downtime_hours != null && <p className="text-xs text-muted" style={{ marginTop: 2 }}>Downtime: {evt.downtime_hours}h</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
