export default function RegulationCard({ regulation }) {
  const score = regulation.compliance_score || 0;
  return (
    <div className="card card-interactive">
      <div className="flex justify-between items-start" style={{ marginBottom: 'var(--spacing-md)' }}>
        <div>
          <p className="font-mono font-semibold text-sm" style={{ color: 'var(--color-accent-primary)' }}>{regulation.regulation_code}</p>
          <p className="text-sm" style={{ marginTop: 2 }}>{regulation.regulation_name}</p>
        </div>
        <span className="font-semibold" style={{ color: score >= 0.8 ? 'var(--color-success)' : score >= 0.6 ? 'var(--color-warning)' : 'var(--color-danger)' }}>
          {Math.round(score * 100)}%
        </span>
      </div>
      <div className="progress-bar" style={{ marginBottom: 'var(--spacing-sm)' }}>
        <div className="progress-fill" style={{ width: `${score * 100}%` }} />
      </div>
      <div className="flex gap-md text-xs">
        <span style={{ color: 'var(--color-success)' }}>✓ {regulation.compliant}</span>
        <span style={{ color: 'var(--color-danger)' }}>✗ {regulation.non_compliant}</span>
        <span style={{ color: 'var(--color-warning)' }}>◐ {regulation.partial}</span>
      </div>
    </div>
  );
}
