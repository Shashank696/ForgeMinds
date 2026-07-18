export default function ComplianceDashboard({ overview }) {
  if (!overview) return null;
  const score = overview.overall_compliance_score || 0;
  const pct = Math.round(score * 100);
  const circumference = 2 * Math.PI * 70;
  const offset = circumference - (score * circumference);
  const color = score >= 0.8 ? 'var(--color-success)' : score >= 0.6 ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div className="flex flex-col items-center" style={{ marginBottom: 'var(--spacing-xl)' }}>
      <div className="compliance-gauge">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="70" fill="none" stroke="var(--color-border)" strokeWidth="8" />
          <circle cx="80" cy="80" r="70" fill="none" stroke={color} strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" />
        </svg>
        <div className="compliance-gauge-value">
          <span className="compliance-gauge-percent" style={{ color }}>{pct}%</span>
          <span className="text-xs text-muted">Compliant</span>
        </div>
      </div>
    </div>
  );
}
