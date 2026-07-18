import { useState } from 'react';
import { getDocuments, uploadDocument as apiUploadDocument, deleteDocument as apiDeleteDocument } from '../services/api';

export default function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const refreshDocuments = async () => {
    setIsLoading(true);
    try {
      const res = await getDocuments();
      setDocuments(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadDocument = async (data) => {
    setIsLoading(true);
    try {
      await apiUploadDocument(data);
      await refreshDocuments();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDocument = async (id) => {
    setIsLoading(true);
    try {
      await apiDeleteDocument(id);
      await refreshDocuments();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return { documents, isLoading, uploadDocument, deleteDocument, refreshDocuments };
}
