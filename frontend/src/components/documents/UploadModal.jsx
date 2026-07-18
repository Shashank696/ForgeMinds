import { useState } from 'react';
import { X } from 'lucide-react';
import FileUploader from '../common/FileUploader';
import { DOCUMENT_CATEGORY_LABELS } from '../../utils/constants';

export default function UploadModal({ isOpen, onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [category, setCategory] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    if (category) formData.append('category', category);
    try {
      await onUpload(formData, setProgress);
      setFile(null);
      setCategory('');
      setProgress(0);
      onClose();
    } catch (e) { /* handled by hook */ }
    setUploading(false);
  };

  return (
    <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal">
        <div className="modal-header">
          <h3>Upload Document</h3>
          <button className="btn btn-ghost btn-icon" onClick={onClose}><X size={18} /></button>
        </div>
        <div className="modal-body">
          <FileUploader onFileSelect={setFile} />
          {file && (
            <div style={{ marginTop: 'var(--spacing-md)' }}>
              <p className="text-sm font-medium">{file.name}</p>
              <p className="text-xs text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
          <div className="form-group" style={{ marginTop: 'var(--spacing-lg)' }}>
            <label className="form-label">Category</label>
            <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">Auto-detect</option>
              {Object.entries(DOCUMENT_CATEGORY_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          {uploading && (
            <div style={{ marginTop: 'var(--spacing-md)' }}>
              <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }} /></div>
              <p className="text-xs text-muted" style={{ marginTop: 4 }}>{progress}% uploaded</p>
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={uploading}>Cancel</button>
          <button className="btn btn-primary" onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  );
}
