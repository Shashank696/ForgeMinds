import { FileText, Eye, Trash2 } from 'lucide-react';
import { DOCUMENT_CATEGORY_LABELS } from '../../utils/constants';
import { formatDate, formatFileSize, getStatusBadgeClass, capitalize } from '../../utils/formatters';

export default function DocumentList({ documents = [], onDelete, onView }) {
  if (!documents.length) {
    return (
      <div className="empty-state">
        <FileText size={48} />
        <h3>No documents yet</h3>
        <p>Upload your first document to get started</p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Document</th>
            <th>Category</th>
            <th>Status</th>
            <th>Entities</th>
            <th>Size</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>
                <div className="flex items-center gap-sm">
                  <FileText size={16} className="text-muted" />
                  <span className="font-medium truncate" style={{ maxWidth: 200 }}>{doc.original_filename || doc.filename}</span>
                </div>
              </td>
              <td><span className="badge badge-primary">{DOCUMENT_CATEGORY_LABELS[doc.document_category] || capitalize(doc.document_category)}</span></td>
              <td><span className={`badge ${getStatusBadgeClass(doc.upload_status)}`}>{capitalize(doc.upload_status)}</span></td>
              <td>{doc.entity_count}</td>
              <td className="text-muted">{formatFileSize(doc.file_size_bytes)}</td>
              <td className="text-muted">{formatDate(doc.created_at)}</td>
              <td>
                <div className="flex gap-xs">
                  <button className="btn btn-ghost btn-sm" onClick={() => onView?.(doc.id)} title="View"><Eye size={15} /></button>
                  <button className="btn btn-ghost btn-sm" onClick={() => { if (window.confirm('Delete this document?')) onDelete?.(doc.id); }} title="Delete"><Trash2 size={15} /></button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
