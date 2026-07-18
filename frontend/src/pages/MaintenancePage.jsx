import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import useMaintenance from '../hooks/useMaintenance';
import MaintenanceDashboard from '../components/maintenance/MaintenanceDashboard';
import EquipmentCard from '../components/maintenance/EquipmentCard';
import PredictiveAlert from '../components/maintenance/PredictiveAlert';
import ConfidenceBadge from '../components/common/ConfidenceBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function MaintenancePage() {
  const { predictions, alerts, rcaResult, isLoading, isAnalyzing, loadPredictions, loadAlerts, runRCA } = useMaintenance();
  const [activeTab, setActiveTab] = useState('predictions');
  const [rcaForm, setRcaForm] = useState({ equipment_id: '', failure_description: '', failure_date: '' });

  useEffect(() => {
    loadPredictions();
    loadAlerts();
  }, [loadPredictions, loadAlerts]);

  const handleRCA = () => {
    if (!rcaForm.failure_description) return;
    runRCA(rcaForm);
  };

  const tabs = [
    { id: 'predictions', label: 'Predictions' },
    { id: 'alerts', label: `Alerts (${alerts.length})` },
    { id: 'rca', label: 'Root Cause Analysis' },
  ];

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Maintenance Intelligence</h1>
          <p className="page-subtitle">Predictive maintenance and root cause analysis</p>
        </div>
        <Link to="/maintenance/rca" className="btn btn-primary">Run RCA</Link>
      </div>

      <div className="tabs">
        {tabs.map((t) => (
          <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {isLoading ? <LoadingSpinner message="Loading maintenance data..." /> : (
        <>
          {activeTab === 'predictions' && (
            <div>
              <MaintenanceDashboard predictions={predictions} alerts={alerts} />
              <div className="flex flex-col gap-md">
                {predictions.map((p, i) => <EquipmentCard key={i} prediction={p} />)}
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="flex flex-col gap-md">
              {alerts.length === 0 ? (
                <div className="empty-state"><h3>No active alerts</h3><p>All systems operating normally</p></div>
              ) : (
                alerts.sort((a, b) => { const o = { critical: 0, high: 1, medium: 2, low: 3 }; return (o[a.severity] || 4) - (o[b.severity] || 4); })
                  .map((a) => <PredictiveAlert key={a.id} alert={a} />)
              )}
            </div>
          )}

          {activeTab === 'rca' && (
            <div>
              <div className="card" style={{ maxWidth: 600, marginBottom: 'var(--spacing-xl)' }}>
                <h4 style={{ marginBottom: 'var(--spacing-md)' }}>Quick Root Cause Analysis</h4>
                <div className="form-group" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <label className="form-label">Equipment Tag</label>
                  <input className="form-input" placeholder="e.g. P-101" value={rcaForm.equipment_id} onChange={(e) => setRcaForm({ ...rcaForm, equipment_id: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <label className="form-label">Failure Description</label>
                  <textarea className="form-textarea" placeholder="Describe the failure event..." value={rcaForm.failure_description} onChange={(e) => setRcaForm({ ...rcaForm, failure_description: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <label className="form-label">Failure Date</label>
                  <input className="form-input" type="date" value={rcaForm.failure_date} onChange={(e) => setRcaForm({ ...rcaForm, failure_date: e.target.value })} />
                </div>
                <button className="btn btn-primary" onClick={handleRCA} disabled={isAnalyzing || !rcaForm.failure_description}>
                  {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
                </button>
              </div>

              {rcaResult && (
                <div className="animate-fade-in-up">
                  <h4 className="section-title">Root Causes</h4>
                  <div className="flex flex-col gap-md" style={{ marginBottom: 'var(--spacing-xl)' }}>
                    {rcaResult.root_causes?.map((rc, i) => (
                      <div key={i} className="card">
                        <div className="flex justify-between items-start">
                          <p className="font-medium">{rc.cause}</p>
                          <ConfidenceBadge score={rc.confidence} />
                        </div>
                      </div>
                    ))}
                  </div>
                  {rcaResult.recommended_actions?.length > 0 && (
                    <div className="card">
                      <h4 className="text-sm font-semibold" style={{ marginBottom: 'var(--spacing-md)' }}>Recommended Actions</h4>
                      <ol style={{ paddingLeft: 'var(--spacing-lg)' }}>
                        {rcaResult.recommended_actions.map((a, i) => <li key={i} className="text-sm" style={{ marginBottom: 'var(--spacing-sm)' }}>{a}</li>)}
                      </ol>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
