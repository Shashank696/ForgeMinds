import { X } from 'lucide-react';
import { ENTITY_TYPE_COLORS, ENTITY_TYPE_LABELS } from '../../utils/constants';
import { capitalize } from '../../utils/formatters';

export default function NodeDetail({ node, onClose }) {
  if (!node) return null;
  const color = ENTITY_TYPE_COLORS[node.entity_type] || '#666';

  return (
    <div className="animate-slide-in-right" style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-lg)', marginTop: 'var(--spacing-lg)' }}>
      <div className="flex justify-between items-center" style={{ marginBottom: 'var(--spacing-md)' }}>
        <span className="badge" style={{ background: `${color}22`, color }}>{ENTITY_TYPE_LABELS[node.entity_type] || 'Entity'}</span>
        <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
      </div>
      <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>{node.name}</h3>
      <p className="text-sm text-muted" style={{ marginBottom: 'var(--spacing-md)' }}>{node.connection_count || 0} connections</p>

      {node.properties && Object.keys(node.properties).length > 0 && (
        <div>
          <p className="text-xs font-semibold text-muted" style={{ textTransform: 'uppercase', marginBottom: 'var(--spacing-sm)' }}>Properties</p>
          {Object.entries(node.properties).map(([k, v]) => (
            <div key={k} className="flex justify-between" style={{ padding: '4px 0', borderBottom: '1px solid var(--color-border)' }}>
              <span className="text-xs text-muted">{capitalize(k)}</span>
              <span className="text-xs font-medium">{String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
