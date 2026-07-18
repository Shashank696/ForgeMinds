import { Link } from 'react-router-dom';
import { FileUp, MessageSquare, Wrench, Shield } from 'lucide-react';

const actions = [
  { to: '/documents', icon: FileUp, title: 'Upload Document', desc: 'Ingest new files', color: 'var(--color-accent-primary)' },
  { to: '/chat', icon: MessageSquare, title: 'Ask AI Copilot', desc: 'Query your knowledge base', color: 'var(--color-accent-secondary)' },
  { to: '/maintenance/rca', icon: Wrench, title: 'Run RCA', desc: 'Root cause analysis', color: 'var(--color-warning)' },
  { to: '/compliance', icon: Shield, title: 'Check Compliance', desc: 'Regulatory gap analysis', color: 'var(--color-success)' },
];

export default function QuickActions() {
  return (
    <div className="grid grid-4 gap-md">
      {actions.map((a) => (
        <Link key={a.to} to={a.to} className="card card-interactive" style={{ textDecoration: 'none' }}>
          <div className="flex flex-col items-center gap-sm" style={{ padding: 'var(--spacing-sm)', textAlign: 'center' }}>
            <div style={{ width: 40, height: 40, borderRadius: 'var(--radius-lg)', background: `${a.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <a.icon size={20} style={{ color: a.color }} />
            </div>
            <span className="font-medium text-sm">{a.title}</span>
            <span className="text-xs text-muted">{a.desc}</span>
          </div>
        </Link>
      ))}
    </div>
  );
}
