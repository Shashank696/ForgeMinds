import { formatScore, getConfidenceColor } from '../../utils/formatters';

export default function ConfidenceBadge({ score }) {
  if (score == null) return null;
  const color = getConfidenceColor(score);
  return (
    <span className="badge" style={{ background: `${color}22`, color }}>
      {formatScore(score)} confidence
    </span>
  );
}
