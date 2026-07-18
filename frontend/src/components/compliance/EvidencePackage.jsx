import { Package } from 'lucide-react';

export default function EvidencePackage({ regulationCode, onGenerate }) {
  return (
    <div className="card">
      <div className="flex items-center gap-md">
        <div style={{ width: 40, height: 40, borderRadius: 'var(--radius-md)', background: 'var(--color-accent-primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Package size={20} style={{ color: 'var(--color-accent-primary)' }} />
        </div>
        <div className="flex-1">
          <p className="font-medium text-sm">{regulationCode} Evidence Package</p>
          <p className="text-xs text-muted">Generate a downloadable evidence package for audit</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => onGenerate?.(regulationCode)}>Generate</button>
      </div>
    </div>
  );
}
