import { getStatusBadgeClass, capitalize, truncateText, formatDate } from '../../utils/formatters';
import { AlertTriangle } from 'lucide-react';

export default function GapHeatmap({ gaps = [] }) {
  if (!gaps.length) {
    return <div className="empty-state"><AlertTriangle size={40} /><h3>No compliance gaps</h3><p>All requirements are met</p></div>;
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Regulation</th>
            <th>Requirement</th>
            <th>Status</th>
            <th>Due Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {gaps.map((g) => (
            <tr key={g.id}>
              <td><span className="font-mono text-sm" style={{ color: 'var(--color-accent-primary)' }}>{g.regulation_code}</span></td>
              <td className="text-sm">{truncateText(g.requirement_text, 60)}</td>
              <td><span className={`badge ${getStatusBadgeClass(g.compliance_status)}`}>{capitalize(g.compliance_status)}</span></td>
              <td className="text-sm text-muted">{formatDate(g.due_date)}</td>
              <td className="text-sm">{truncateText(g.remediation_action, 40)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
