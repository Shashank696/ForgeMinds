import { useState, useCallback } from 'react';
import { fetchMaintenancePredictions, fetchMaintenanceAlerts, requestRCA } from '../services/api';
import toast from 'react-hot-toast';

export default function useMaintenance() {
  const [predictions, setPredictions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [rcaResult, setRcaResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const loadPredictions = useCallback(async (params = {}) => {
    setIsLoading(true);
    try {
      const data = await fetchMaintenancePredictions(params);
      setPredictions(data.predictions || []);
    } catch (e) {
      toast.error('Failed to load predictions');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      const data = await fetchMaintenanceAlerts();
      setAlerts(data.alerts || []);
    } catch (e) {
      toast.error('Failed to load alerts');
    }
  }, []);

  const runRCA = useCallback(async (data) => {
    setIsAnalyzing(true);
    setRcaResult(null);
    try {
      const result = await requestRCA(data);
      setRcaResult(result);
      toast.success('Root cause analysis complete');
      return result;
    } catch (e) {
      toast.error('RCA analysis failed');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  return {
    predictions, alerts, rcaResult, isLoading, isAnalyzing,
    loadPredictions, loadAlerts, runRCA, setRcaResult,
  };
}
