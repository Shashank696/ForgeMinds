import { getRiskColor, getRiskBadgeClass, capitalize, formatScore } from '../../utils/formatters';
import ConfidenceBadge from '../common/ConfidenceBadge';

export default function EquipmentCard({ prediction }) {
  const color = getRiskColor(prediction.risk_level);
  return (
    <div className="card animate-fade-in-up" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="flex justify-between items-start" style={{ marginBottom: 'var(--spacing-md)' }}>
        <div>
          <div className="flex items-center gap-sm">
            <span className="font-mono font-semibold" style={{ color: 'var(--color-accent-primary)' }}>{prediction.equipment_tag}</span>
            <span className={`badge ${getRiskBadgeClass(prediction.risk_level)}`}>{capitalize(prediction.risk_level)}</span>
          </div>
          <p className="text-sm font-medium" style={{ marginTop: 4 }}>{prediction.prediction_type}</p>
        </div>
        <ConfidenceBadge score={prediction.confidence} />
      </div>
      <p className="text-sm text-secondary" style={{ marginBottom: 'var(--spacing-sm)' }}>{prediction.predicted_failure_mode}</p>
      <div className="card" style={{ background: 'var(--color-bg-tertiary)', padding: 'var(--spacing-md)', marginBottom: 'var(--spacing-sm)' }}>
        <p className="text-xs font-semibold text-muted" style={{ marginBottom: 2 }}>Recommended Action</p>
        <p className="text-sm">{prediction.recommended_action}</p>
      </div>
      {prediction.estimated_date && (
        <p className="text-xs text-muted">Estimated failure: {prediction.estimated_date}</p>
      )}
    </div>
  );
}
