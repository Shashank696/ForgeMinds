import { formatRelativeTime } from '../../utils/formatters';
import { FileUp, MessageSquare, AlertTriangle, Shield } from 'lucide-react';

const icons = { upload: FileUp, query: MessageSquare, alert: AlertTriangle, compliance: Shield };

export default function AnalyticsDashboard({ data }) {
  if (!data) return null;

  return (
    <div className="card" style={{ marginTop: 'var(--spacing-xl)' }}>
      <h4 className="section-title" style={{ marginBottom: 'var(--spacing-md)' }}>Recent Activity</h4>
      <div className="flex flex-col gap-sm">
        {(data.recent_activity || []).map((a, i) => {
          const Icon = icons[a.type] || MessageSquare;
          return (
            <div key={i} className="flex items-center gap-md" style={{ padding: '4px 0' }}>
              <Icon size={14} className="text-muted" />
              <span className="text-sm flex-1">{a.description}</span>
              <span className="text-xs text-muted">{formatRelativeTime(a.timestamp)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
