import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, AlertTriangle, FileText, Info } from 'lucide-react';
import { fetchDocument } from '../services/api';
import { formatDate, capitalize } from '../utils/formatters';
import LoadingSpinner from '../components/common/LoadingSpinner';
import DocumentViewer from '../components/documents/DocumentViewer';
import { toast } from 'react-hot-toast';

const DocumentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const loadDocument = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchDocument(id);
        setDocument(data);
      } catch (err) {
        setError(err?.message || 'Failed to load document.');
      } finally {
        setIsLoading(false);
      }
    };
    loadDocument();
  }, [id]);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      // API call would go here: await deleteDocument(id);
      toast.success('Document deleted successfully.');
      navigate('/documents');
    } catch (err) {
      toast.error(err?.message || 'Failed to delete document.');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-loading">
        <LoadingSpinner />
        <p>Loading document…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error">
        <AlertTriangle size={48} />
        <h2>Error Loading Document</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/documents')}>
          <ArrowLeft size={18} /> Back to Documents
        </button>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="page-error">
        <Info size={48} />
        <h2>Document Not Found</h2>
        <p>The requested document could not be found.</p>
        <button className="btn btn-primary" onClick={() => navigate('/documents')}>
          <ArrowLeft size={18} /> Back to Documents
        </button>
      </div>
    );
  }

  return (
    <div className="document-detail-page animate-fade-in">
      <div className="page-header-row">
        <button className="btn btn-ghost" onClick={() => navigate('/documents')}>
          <ArrowLeft size={18} />
          Back to Documents
        </button>

        <div className="page-header-actions">
          {!showDeleteConfirm ? (
            <button
              className="btn btn-danger"
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 size={16} />
              Delete
            </button>
          ) : (
            <div className="delete-confirm">
              <span>Are you sure?</span>
              <button
                className="btn btn-danger btn-sm"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting…' : 'Confirm Delete'}
              </button>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="document-detail-header">
        <div className="document-detail-icon">
          <FileText size={28} />
        </div>
        <div className="document-detail-info">
          <h1>{document.title || document.name || 'Untitled Document'}</h1>
          <div className="document-detail-meta">
            {document.category && (
              <span className="badge badge-secondary">{capitalize(document.category)}</span>
            )}
            {document.processing_stage && (
              <span className="badge badge-info">{capitalize(document.processing_stage)}</span>
            )}
            {document.created_at && (
              <span className="meta-item">{formatDate(document.created_at)}</span>
            )}
          </div>
        </div>
      </div>

      <div className="document-viewer-wrapper">
        <DocumentViewer document={document} />
      </div>
    </div>
  );
};

export default DocumentDetailPage;
