import { getRiskColor, getRiskBadgeClass, capitalize, formatNumber } from '../../utils/formatters';

export default function MaintenanceDashboard({ predictions = [], alerts = [] }) {
  const critical = predictions.filter((p) => p.risk_level === 'critical').length;
  const high = predictions.filter((p) => p.risk_level === 'high').length;
  const medium = predictions.filter((p) => p.risk_level === 'medium').length;
  const total = predictions.length;

  const stats = [
    { label: 'Total Predictions', value: total, color: 'var(--color-accent-primary)' },
    { label: 'Critical', value: critical, color: 'var(--color-danger)' },
    { label: 'High', value: high, color: '#f97316' },
    { label: 'Active Alerts', value: alerts.length, color: 'var(--color-warning)' },
  ];

  return (
    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
      <div className="stats-grid">
        {stats.map((s) => (
          <div key={s.label} className="card" style={{ borderLeft: `4px solid ${s.color}` }}>
            <p className="text-xs text-muted">{s.label}</p>
            <p style={{ fontSize: 'var(--font-2xl)', fontWeight: 700 }}>{s.value}</p>
          </div>
        ))}
      </div>
      {total > 0 && (
        <div className="flex gap-xs" style={{ marginTop: 'var(--spacing-md)', height: 6, borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
          {critical > 0 && <div style={{ flex: critical, background: 'var(--color-danger)' }} />}
          {high > 0 && <div style={{ flex: high, background: '#f97316' }} />}
          {medium > 0 && <div style={{ flex: medium, background: 'var(--color-warning)' }} />}
          {(total - critical - high - medium) > 0 && <div style={{ flex: total - critical - high - medium, background: 'var(--color-success)' }} />}
        </div>
      )}
    </div>
  );
}
