import { useState, useEffect } from 'react';
import useCompliance from '../hooks/useCompliance';
import ComplianceDashboard from '../components/compliance/ComplianceDashboard';
import RegulationCard from '../components/compliance/RegulationCard';
import GapHeatmap from '../components/compliance/GapHeatmap';
import EvidencePackage from '../components/compliance/EvidencePackage';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function CompliancePage() {
  const { overview, gaps, isLoading, loadOverview, loadGaps, runAssessment } = useCompliance();
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadOverview();
    loadGaps();
  }, [loadOverview, loadGaps]);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'gaps', label: `Gaps (${gaps.length})` },
    { id: 'regulations', label: 'Regulations' },
  ];

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Compliance Intelligence</h1>
          <p className="page-subtitle">Regulatory compliance monitoring and gap analysis</p>
        </div>
        <button className="btn btn-primary" onClick={() => runAssessment({})}>Run Assessment</button>
      </div>

      <div className="tabs">
        {tabs.map((t) => <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>{t.label}</button>)}
      </div>

      {isLoading ? <LoadingSpinner message="Loading compliance data..." /> : (
        <>
          {activeTab === 'overview' && (
            <div>
              <ComplianceDashboard overview={overview} />
              <div className="grid grid-2 gap-md">
                {overview?.by_regulation?.map((r) => <RegulationCard key={r.regulation_code} regulation={r} />)}
              </div>
              {overview?.by_regulation?.length > 0 && (
                <div style={{ marginTop: 'var(--spacing-xl)' }}>
                  <h4 className="section-title">Evidence Packages</h4>
                  <div className="flex flex-col gap-sm">
                    {overview.by_regulation.map((r) => <EvidencePackage key={r.regulation_code} regulationCode={r.regulation_code} />)}
                  </div>
                </div>
              )}
            </div>
          )}
          {activeTab === 'gaps' && <GapHeatmap gaps={gaps} />}
          {activeTab === 'regulations' && (
            <div className="grid grid-2 gap-md">
              {overview?.by_regulation?.map((r) => <RegulationCard key={r.regulation_code} regulation={r} />)}
            </div>
          )}
        </>
      )}
    </div>
  );
}
