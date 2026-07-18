import { TrendingUp, TrendingDown } from 'lucide-react';

export default function StatCard({ title, value, icon: Icon, trend, color = 'var(--color-accent-primary)', subtitle }) {
  return (
    <div className="card card-glass animate-fade-in-up">
      <div className="flex items-center gap-lg">
        <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-lg)', background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          {Icon && <Icon size={22} style={{ color }} />}
        </div>
        <div className="flex-1">
          <p className="text-sm text-secondary">{title}</p>
          <div className="flex items-center gap-sm">
            <h3 style={{ fontSize: 'var(--font-2xl)', fontWeight: 700 }}>{value}</h3>
            {trend != null && (
              <span className="flex items-center gap-xs text-xs" style={{ color: trend >= 0 ? 'var(--color-success)' : 'var(--color-danger)' }}>
                {trend >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {Math.abs(trend)}%
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
}
