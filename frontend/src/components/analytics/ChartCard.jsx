export default function ChartCard({ title, subtitle, children }) {
  return (
    <div className="card">
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <h4 className="text-base font-semibold">{title}</h4>
        {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
