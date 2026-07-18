import { FileUp, MessageSquare, AlertTriangle, Shield } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

const icons = { upload: FileUp, query: MessageSquare, alert: AlertTriangle, compliance: Shield };

export default function RecentActivity({ activities = [] }) {
  if (!activities.length) return <p className="text-sm text-muted">No recent activity</p>;
  return (
    <div className="flex flex-col gap-sm">
      {activities.map((a, i) => {
        const Icon = icons[a.type] || MessageSquare;
        return (
          <div key={i} className="flex items-center gap-md" style={{ padding: 'var(--spacing-sm) 0' }}>
            <div style={{ width: 32, height: 32, borderRadius: 'var(--radius-md)', background: 'var(--color-bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Icon size={14} className="text-secondary" />
            </div>
            <p className="flex-1 text-sm truncate">{a.description}</p>
            <span className="text-xs text-muted flex-shrink-0">{formatRelativeTime(a.timestamp)}</span>
          </div>
        );
      })}
    </div>
  );
}
