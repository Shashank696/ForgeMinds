import { useState, useCallback } from 'react';
import { fetchDocuments, uploadDocument as apiUpload, deleteDocument as apiDelete, fetchDocument } from '../services/api';
import toast from 'react-hot-toast';

export default function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const refreshDocuments = useCallback(async (params = {}) => {
    setIsLoading(true);
    try {
      const data = await fetchDocuments(params);
      setDocuments(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadDoc = useCallback(async (formData, onProgress) => {
    try {
      await apiUpload(formData, (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      });
      toast.success('Document uploaded successfully');
      await refreshDocuments();
    } catch (e) {
      toast.error('Upload failed');
      throw e;
    }
  }, [refreshDocuments]);

  const deleteDoc = useCallback(async (id) => {
    try {
      await apiDelete(id);
      toast.success('Document deleted');
      await refreshDocuments();
    } catch (e) {
      toast.error('Delete failed');
    }
  }, [refreshDocuments]);

  const getDocumentDetail = useCallback(async (id) => {
    try {
      return await fetchDocument(id);
    } catch (e) {
      toast.error('Failed to load document details');
      return null;
    }
  }, []);

  return { documents, total, isLoading, uploadDocument: uploadDoc, deleteDoc, refreshDocuments, getDocumentDetail };
}
