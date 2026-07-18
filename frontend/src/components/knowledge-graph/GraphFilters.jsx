import { useState } from 'react';
import { ENTITY_TYPE_LABELS, ENTITY_TYPE_COLORS } from '../../utils/constants';

export default function GraphFilters({ onFilter, stats }) {
  const [search, setSearch] = useState('');
  const [activeTypes, setActiveTypes] = useState(Object.keys(ENTITY_TYPE_LABELS));
  const [depth, setDepth] = useState(2);

  const toggleType = (type) => {
    setActiveTypes((prev) => prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]);
  };

  const handleApply = () => {
    onFilter?.({ search, types: activeTypes, depth });
  };

  return (
    <div>
      <input className="form-input" placeholder="Search nodes..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ marginBottom: 'var(--spacing-md)' }} />

      <p className="text-xs font-semibold text-muted" style={{ marginBottom: 'var(--spacing-sm)', textTransform: 'uppercase' }}>Entity Types</p>
      <div className="flex flex-col gap-xs" style={{ marginBottom: 'var(--spacing-md)' }}>
        {Object.entries(ENTITY_TYPE_LABELS).map(([key, label]) => (
          <label key={key} className="flex items-center gap-sm cursor-pointer text-sm">
            <input type="checkbox" checked={activeTypes.includes(key)} onChange={() => toggleType(key)} />
            <span className="kg-legend-dot" style={{ background: ENTITY_TYPE_COLORS[key], width: 8, height: 8, borderRadius: '50%' }} />
            <span className="flex-1">{label}</span>
            {stats?.nodes_by_type?.[key] != null && <span className="text-xs text-muted">{stats.nodes_by_type[key]}</span>}
          </label>
        ))}
      </div>

      <div className="form-group" style={{ marginBottom: 'var(--spacing-md)' }}>
        <label className="form-label">Depth</label>
        <select className="form-select" value={depth} onChange={(e) => setDepth(Number(e.target.value))}>
          <option value={1}>1 hop</option>
          <option value={2}>2 hops</option>
          <option value={3}>3 hops</option>
        </select>
      </div>

      <button className="btn btn-primary w-full" onClick={handleApply}>Apply Filters</button>
    </div>
  );
}
