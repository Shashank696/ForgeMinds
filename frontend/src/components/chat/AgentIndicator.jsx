import { AGENT_TYPE_LABELS, AGENT_TYPE_COLORS } from '../../utils/constants';

export default function AgentIndicator({ agentType }) {
  const color = AGENT_TYPE_COLORS[agentType] || '#6366f1';
  const label = AGENT_TYPE_LABELS[agentType] || 'Auto';
  return (
    <span className="badge" style={{ background: `${color}22`, color, gap: 4 }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: color, display: 'inline-block' }} />
      {label}
    </span>
  );
}
