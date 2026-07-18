import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useDocuments from '../hooks/useDocuments';
import DocumentList from '../components/documents/DocumentList';
import UploadModal from '../components/documents/UploadModal';
import { DOCUMENT_CATEGORY_LABELS } from '../utils/constants';

export default function DocumentsPage() {
  const { documents, isLoading, uploadDocument, deleteDoc, refreshDocuments } = useDocuments();
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const navigate = useNavigate();

  useEffect(() => { refreshDocuments(); }, [refreshDocuments]);

  const filtered = documents.filter((d) => {
    const matchSearch = !search || (d.original_filename || d.filename || '').toLowerCase().includes(search.toLowerCase());
    const matchCat = !category || d.document_category === category;
    return matchSearch && matchCat;
  });

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Documents</h1>
          <p className="page-subtitle">{documents.length} documents in knowledge base</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
          <Plus size={16} /> Upload
        </button>
      </div>

      <div className="flex gap-md" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <input className="form-input" style={{ maxWidth: 300 }} placeholder="Search documents..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="form-select" style={{ maxWidth: 200 }} value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {Object.entries(DOCUMENT_CATEGORY_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-md">{[1,2,3].map(i => <div key={i} className="skeleton skeleton-card" />)}</div>
      ) : (
        <DocumentList documents={filtered} onDelete={deleteDoc} onView={(id) => navigate(`/documents/${id}`)} />
      )}

      <UploadModal isOpen={showUpload} onClose={() => setShowUpload(false)} onUpload={uploadDocument} />
    </div>
  );
}
