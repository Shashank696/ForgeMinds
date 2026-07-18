import { truncateText } from '../../utils/formatters';
import { FileText } from 'lucide-react';

export default function CitationCard({ citation }) {
  if (!citation) return null;
  return (
    <div className="chat-citation">
      <div className="flex items-center gap-sm" style={{ marginBottom: 4 }}>
        <FileText size={12} />
        <span className="font-medium text-sm">{citation.document_title}</span>
        {citation.page_number && <span className="text-xs text-muted">p.{citation.page_number}</span>}
      </div>
      <p className="text-xs text-secondary">{truncateText(citation.chunk_text, 120)}</p>
      <div className="progress-bar" style={{ height: 3, marginTop: 6 }}>
        <div className="progress-fill" style={{ width: `${(citation.relevance_score || 0) * 100}%` }} />
      </div>
    </div>
  );
}
