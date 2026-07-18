import { PROCESSING_STAGE_LABELS, PROCESSING_STAGES } from '../../utils/constants';
import { formatDate, formatFileSize, getStatusBadgeClass, capitalize } from '../../utils/formatters';
import { FileText, Tag } from 'lucide-react';
import { ENTITY_TYPE_COLORS } from '../../utils/constants';

const stageOrder = [PROCESSING_STAGES.UPLOADED, PROCESSING_STAGES.OCR_COMPLETE, PROCESSING_STAGES.ENTITIES_EXTRACTED, PROCESSING_STAGES.EMBEDDED, PROCESSING_STAGES.GRAPH_LINKED];

export default function DocumentViewer({ document: doc }) {
  if (!doc) return null;
  const currentIdx = stageOrder.indexOf(doc.processing_stage);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-md" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <div style={{ width: 48, height: 48, borderRadius: 'var(--radius-lg)', background: 'var(--color-accent-primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <FileText size={24} style={{ color: 'var(--color-accent-primary)' }} />
        </div>
        <div>
          <h3>{doc.original_filename || doc.filename}</h3>
          <div className="flex gap-sm" style={{ marginTop: 4 }}>
            <span className="badge badge-primary">{capitalize(doc.document_category)}</span>
            <span className={`badge ${getStatusBadgeClass(doc.upload_status)}`}>{capitalize(doc.upload_status)}</span>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Processing Pipeline</h4>
        <div className="flex items-center gap-sm" style={{ overflow: 'auto' }}>
          {stageOrder.map((stage, i) => (
            <div key={stage} className="flex items-center gap-xs">
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: i <= currentIdx ? 'var(--color-success)' : 'var(--color-border)', flexShrink: 0 }} />
              <span className={`text-xs ${i <= currentIdx ? '' : 'text-muted'}`} style={{ whiteSpace: 'nowrap' }}>{PROCESSING_STAGE_LABELS[stage]}</span>
              {i < stageOrder.length - 1 && <div style={{ width: 20, height: 2, background: i < currentIdx ? 'var(--color-success)' : 'var(--color-border)' }} />}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-3" style={{ gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
        <div className="card"><p className="text-xs text-muted">File Size</p><p className="font-medium">{formatFileSize(doc.file_size_bytes)}</p></div>
        <div className="card"><p className="text-xs text-muted">Pages</p><p className="font-medium">{doc.page_count || '—'}</p></div>
        <div className="card"><p className="text-xs text-muted">Chunks</p><p className="font-medium">{doc.chunk_count || 0}</p></div>
      </div>

      {doc.extracted_text && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Extracted Text</h4>
          <pre className="font-mono text-xs" style={{ whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto', color: 'var(--color-text-secondary)', lineHeight: 1.6, background: 'var(--color-bg-primary)', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-md)' }}>
            {doc.extracted_text}
          </pre>
        </div>
      )}

      {doc.entities?.length > 0 && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Extracted Entities ({doc.entities.length})</h4>
          <div className="flex flex-wrap gap-sm">
            {doc.entities.map((ent) => (
              <span key={ent.id} className="badge" style={{ background: `${ENTITY_TYPE_COLORS[ent.entity_type] || '#666'}22`, color: ENTITY_TYPE_COLORS[ent.entity_type] || '#666' }}>
                <Tag size={10} /> {ent.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {doc.linked_equipment?.length > 0 && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Linked Equipment</h4>
          <div className="flex flex-col gap-sm">
            {doc.linked_equipment.map((eq) => (
              <div key={eq.id} className="flex items-center gap-md" style={{ padding: 'var(--spacing-sm)', background: 'var(--color-bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                <span className="font-mono font-semibold text-sm" style={{ color: 'var(--color-accent-primary)' }}>{eq.tag}</span>
                <span className="text-sm">{eq.name}</span>
                <span className="badge badge-secondary text-xs">{capitalize(eq.equipment_type)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {doc.metadata && Object.keys(doc.metadata).length > 0 && (
        <div className="card">
          <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Metadata</h4>
          <div className="grid grid-2 gap-sm">
            {Object.entries(doc.metadata).map(([k, v]) => (
              <div key={k}><p className="text-xs text-muted">{capitalize(k)}</p><p className="text-sm font-medium">{String(v)}</p></div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
