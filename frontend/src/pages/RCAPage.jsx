import React, { useState, useEffect } from 'react';
import {
  Search, AlertTriangle, Wrench, Calendar, FileText, ArrowRight,
  CheckCircle2, Lightbulb, Link2, Loader2, Activity, Target
} from 'lucide-react';
import useMaintenance from '../hooks/useMaintenance';
import { fetchEquipment } from '../services/api';
import { capitalize, formatDate } from '../utils/formatters';
import ConfidenceBadge from '../components/common/ConfidenceBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';

const RCAPage = () => {
  const { rcaResult, isAnalyzing, runRCA, setRcaResult } = useMaintenance();

  const [equipmentList, setEquipmentList] = useState([]);
  const [isLoadingEquipment, setIsLoadingEquipment] = useState(true);

  const [selectedEquipment, setSelectedEquipment] = useState('');
  const [failureDescription, setFailureDescription] = useState('');
  const [failureDate, setFailureDate] = useState('');
  const [formError, setFormError] = useState('');

  useEffect(() => {
    const loadEquipment = async () => {
      setIsLoadingEquipment(true);
      try {
        const data = await fetchEquipment();
        const items = Array.isArray(data) ? data : data?.items || data?.equipment || [];
        setEquipmentList(items);
      } catch (err) {
        console.error('Failed to load equipment:', err);
        setEquipmentList([]);
      } finally {
        setIsLoadingEquipment(false);
      }
    };
    loadEquipment();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!failureDescription.trim()) {
      setFormError('Please provide a failure description.');
      return;
    }

    try {
      await runRCA({
        equipment_id: selectedEquipment || undefined,
        failure_description: failureDescription.trim(),
        failure_date: failureDate || undefined,
      });
    } catch (err) {
      setFormError(err?.message || 'Analysis failed. Please try again.');
    }
  };

  const rootCauses = rcaResult?.root_causes || rcaResult?.causes || [];
  const recommendedActions = rcaResult?.recommended_actions || rcaResult?.actions || [];
  const relatedEquipment = rcaResult?.related_equipment || [];

  return (
    <div className="rca-page animate-fade-in">
      <div className="page-header">
        <div className="page-header-text">
          <h1>
            <Target size={28} />
            Root Cause Analysis
          </h1>
          <p>AI-powered failure analysis to identify root causes, recommend corrective actions, and prevent recurrence.</p>
        </div>
      </div>

      <div className="rca-layout">
        <div className="rca-form-section">
          <div className="card">
            <div className="card-header">
              <h3>
                <Search size={18} />
                Analysis Parameters
              </h3>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit} className="rca-form">
                <div className="form-group">
                  <label htmlFor="rca-equipment">Equipment (Optional)</label>
                  <div className="input-with-icon">
                    <Wrench size={18} className="input-icon" />
                    <select
                      id="rca-equipment"
                      value={selectedEquipment}
                      onChange={(e) => setSelectedEquipment(e.target.value)}
                      disabled={isLoadingEquipment}
                    >
                      <option value="">
                        {isLoadingEquipment ? 'Loading equipment…' : 'Select equipment (optional)'}
                      </option>
                      {equipmentList.map((eq) => (
                        <option key={eq.id || eq.equipment_id} value={eq.id || eq.equipment_id}>
                          {eq.name || eq.equipment_name || eq.tag || `Equipment ${eq.id}`}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="rca-description">Failure Description *</label>
                  <textarea
                    id="rca-description"
                    rows={5}
                    placeholder="Describe the failure event in detail. Include symptoms, conditions, and any observations…"
                    value={failureDescription}
                    onChange={(e) => setFailureDescription(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="rca-date">Failure Date (Optional)</label>
                  <div className="input-with-icon">
                    <Calendar size={18} className="input-icon" />
                    <input
                      id="rca-date"
                      type="date"
                      value={failureDate}
                      onChange={(e) => setFailureDate(e.target.value)}
                    />
                  </div>
                </div>

                {formError && (
                  <div className="form-error animate-fade-in">
                    <AlertTriangle size={16} />
                    <span>{formError}</span>
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary btn-lg"
                  disabled={isAnalyzing}
                  style={{ width: '100%' }}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 size={18} className="spin" />
                      Running Analysis…
                    </>
                  ) : (
                    <>
                      <Activity size={18} />
                      Run Analysis
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="rca-results-section">
          {isAnalyzing && (
            <div className="rca-analyzing-state">
              <LoadingSpinner />
              <h3>Analyzing Failure…</h3>
              <p>The AI is examining documents, maintenance history, and failure patterns to identify root causes.</p>
            </div>
          )}

          {!isAnalyzing && !rcaResult && (
            <div className="rca-empty-state">
              <Target size={56} />
              <h3>Configure & Run Analysis</h3>
              <p>Fill in the failure details on the left and click "Run Analysis" to get AI-driven root cause insights.</p>
            </div>
          )}

          {!isAnalyzing && rcaResult && (
            <div className="rca-results animate-fade-in-up">
              {/* Root Causes */}
              {rootCauses.length > 0 && (
                <div className="card rca-result-card">
                  <div className="card-header">
                    <h3>
                      <AlertTriangle size={18} />
                      Root Causes Identified
                    </h3>
                    <span className="badge badge-warning">{rootCauses.length} found</span>
                  </div>
                  <div className="card-body">
                    <div className="rca-causes-list">
                      {rootCauses.map((cause, idx) => (
                        <div
                          className="rca-cause-item animate-fade-in-up"
                          key={idx}
                          style={{ animationDelay: `${idx * 100}ms` }}
                        >
                          <div className="rca-cause-header">
                            <span className="rca-cause-number">{idx + 1}</span>
                            <div className="rca-cause-title">
                              <h4>{cause.cause || cause.title || cause.description || `Root Cause ${idx + 1}`}</h4>
                              {(cause.confidence != null || cause.score != null) && (
                                <ConfidenceBadge score={cause.confidence ?? cause.score} />
                              )}
                            </div>
                          </div>
                          {cause.evidence && (
                            <div className="rca-cause-evidence">
                              <span className="evidence-label">
                                <FileText size={14} /> Evidence
                              </span>
                              <p>{cause.evidence}</p>
                            </div>
                          )}
                          {cause.similar_incidents && cause.similar_incidents.length > 0 && (
                            <div className="rca-cause-similar">
                              <span className="evidence-label">
                                <Link2 size={14} /> Similar Incidents
                              </span>
                              <ul>
                                {cause.similar_incidents.map((incident, i) => (
                                  <li key={i}>
                                    {incident.title || incident.description || incident}
                                    {incident.date && (
                                      <span className="incident-date"> — {formatDate(incident.date)}</span>
                                    )}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Recommended Actions */}
              {recommendedActions.length > 0 && (
                <div className="card rca-result-card animate-fade-in-up" style={{ animationDelay: '200ms' }}>
                  <div className="card-header">
                    <h3>
                      <Lightbulb size={18} />
                      Recommended Actions
                    </h3>
                  </div>
                  <div className="card-body">
                    <ol className="rca-actions-list">
                      {recommendedActions.map((action, idx) => (
                        <li key={idx} className="rca-action-item">
                          <CheckCircle2 size={16} className="action-check" />
                          <span>{typeof action === 'string' ? action : action.description || action.action || action.title}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              )}

              {/* Related Equipment */}
              {relatedEquipment.length > 0 && (
                <div className="card rca-result-card animate-fade-in-up" style={{ animationDelay: '350ms' }}>
                  <div className="card-header">
                    <h3>
                      <Wrench size={18} />
                      Related Equipment at Risk
                    </h3>
                  </div>
                  <div className="card-body">
                    <div className="rca-related-grid">
                      {relatedEquipment.map((eq, idx) => (
                        <div className="rca-related-card" key={eq.id || idx}>
                          <div className="rca-related-icon">
                            <Wrench size={20} />
                          </div>
                          <div className="rca-related-info">
                            <h4>{eq.name || eq.equipment_name || `Equipment ${eq.id}`}</h4>
                            {eq.risk_score != null && (
                              <span className="badge badge-warning">
                                Risk: {(eq.risk_score * 100).toFixed(0)}%
                              </span>
                            )}
                            {eq.reason && <p>{eq.reason}</p>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RCAPage;
