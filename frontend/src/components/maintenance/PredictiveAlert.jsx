import { AlertTriangle, Clock, ShieldAlert, X } from 'lucide-react';
import { getRiskColor, capitalize, formatRelativeTime } from '../../utils/formatters';

const alertIcons = { failure_pattern: AlertTriangle, maintenance_overdue: Clock, compliance_due: ShieldAlert };

export default function PredictiveAlert({ alert, onDismiss }) {
  const color = getRiskColor(alert.severity);
  const Icon = alertIcons[alert.alert_type] || AlertTriangle;

  return (
    <div className="card animate-fade-in-up" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="flex justify-between items-start">
        <div className="flex gap-md items-start">
          <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Icon size={18} style={{ color }} />
          </div>
          <div>
            <h4 className="text-sm font-semibold">{alert.title}</h4>
            <p className="text-sm text-secondary" style={{ marginTop: 4 }}>{alert.description}</p>
            {alert.equipment && (
              <p className="text-xs text-muted" style={{ marginTop: 4 }}>
                <span className="font-mono" style={{ color: 'var(--color-accent-primary)' }}>{alert.equipment.tag}</span> — {alert.equipment.name}
              </p>
            )}
            <p className="text-xs text-muted" style={{ marginTop: 4 }}>{formatRelativeTime(alert.created_at)}</p>
          </div>
        </div>
        {onDismiss && <button className="btn btn-ghost btn-sm" onClick={() => onDismiss(alert.id)}><X size={14} /></button>}
      </div>
    </div>
  );
}
