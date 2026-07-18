import { useState, useCallback } from 'react';
import { fetchComplianceStatus, fetchComplianceGaps, assessCompliance } from '../services/api';
import toast from 'react-hot-toast';

export default function useCompliance() {
  const [overview, setOverview] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadOverview = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchComplianceStatus();
      setOverview(data);
    } catch (e) {
      toast.error('Failed to load compliance status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadGaps = useCallback(async () => {
    try {
      const data = await fetchComplianceGaps();
      setGaps(data.gaps || []);
    } catch (e) {
      toast.error('Failed to load compliance gaps');
    }
  }, []);

  const runAssessment = useCallback(async (data) => {
    try {
      await assessCompliance(data);
      toast.success('Compliance assessment started');
      await loadOverview();
      await loadGaps();
    } catch (e) {
      toast.error('Assessment failed');
    }
  }, [loadOverview, loadGaps]);

  return { overview, gaps, isLoading, loadOverview, loadGaps, runAssessment };
}
