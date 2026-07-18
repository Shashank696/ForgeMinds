import { FileText, Trash2 } from 'lucide-react';
import { DOCUMENT_CATEGORY_LABELS } from '../../utils/constants';
import { formatDate, formatFileSize, getStatusBadgeClass, capitalize, truncateText } from '../../utils/formatters';

export default function DocumentCard({ document: doc, onDelete, onView }) {
  return (
    <div className="card card-interactive" onClick={() => onView?.(doc.id)} style={{ cursor: 'pointer' }}>
      <div className="flex items-center gap-md" style={{ marginBottom: 'var(--spacing-md)' }}>
        <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'var(--color-accent-primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <FileText size={18} style={{ color: 'var(--color-accent-primary)' }} />
        </div>
        <div className="flex-1 overflow-hidden">
          <p className="font-medium text-sm truncate">{truncateText(doc.original_filename || doc.filename, 30)}</p>
          <span className={`badge ${getStatusBadgeClass(doc.upload_status)}`} style={{ fontSize: '0.65rem' }}>{capitalize(doc.upload_status)}</span>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); if (window.confirm('Delete?')) onDelete?.(doc.id); }}>
          <Trash2 size={14} />
        </button>
      </div>
      <div className="flex items-center gap-sm" style={{ flexWrap: 'wrap' }}>
        <span className="badge badge-primary">{DOCUMENT_CATEGORY_LABELS[doc.document_category] || 'Other'}</span>
        <span className="text-xs text-muted">{doc.entity_count} entities</span>
        <span className="text-xs text-muted">{formatFileSize(doc.file_size_bytes)}</span>
        <span className="text-xs text-muted" style={{ marginLeft: 'auto' }}>{formatDate(doc.created_at)}</span>
      </div>
    </div>
  );
}
