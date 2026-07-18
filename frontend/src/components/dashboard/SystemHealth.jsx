const services = ['API Server', 'PostgreSQL', 'Neo4j', 'Qdrant', 'Redis'];

export default function SystemHealth() {
  return (
    <div className="card">
      <h4 className="section-title" style={{ marginBottom: 'var(--spacing-md)' }}>System Health</h4>
      <div className="flex flex-col gap-sm">
        {services.map((s) => (
          <div key={s} className="flex items-center gap-md" style={{ padding: '4px 0' }}>
            <span className="status-dot online" />
            <span className="text-sm">{s}</span>
            <span className="text-xs text-muted" style={{ marginLeft: 'auto' }}>Online</span>
          </div>
        ))}
      </div>
    </div>
  );
}
