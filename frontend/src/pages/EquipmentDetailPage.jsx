import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft, Wrench, Tag, MapPin, Calendar, Clock, AlertTriangle,
  FileText, Activity, Settings, Layers, Hash, Thermometer, Gauge,
  CheckCircle2, XCircle, Info
} from 'lucide-react';
import { fetchEquipmentDetail } from '../services/api';
import { formatDate, formatDateTime, getStatusBadgeClass, getCriticalityColor, capitalize } from '../utils/formatters';
import { EQUIPMENT_TYPE_LABELS, EQUIPMENT_STATUS_LABELS } from '../utils/constants';
import LoadingSpinner from '../components/common/LoadingSpinner';
import FailureTimeline from '../components/maintenance/FailureTimeline';

const EquipmentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [equipment, setEquipment] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadEquipment = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchEquipmentDetail(id);
        setEquipment(data);
      } catch (err) {
        setError(err?.message || 'Failed to load equipment details.');
      } finally {
        setIsLoading(false);
      }
    };
    loadEquipment();
  }, [id]);

  if (isLoading) {
    return (
      <div className="page-loading">
        <LoadingSpinner />
        <p>Loading equipment details…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error">
        <AlertTriangle size={48} />
        <h2>Error Loading Equipment</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/maintenance')}>
          <ArrowLeft size={18} /> Back to Maintenance
        </button>
      </div>
    );
  }

  if (!equipment) {
    return (
      <div className="page-error">
        <Info size={48} />
        <h2>Equipment Not Found</h2>
        <button className="btn btn-primary" onClick={() => navigate('/maintenance')}>
          <ArrowLeft size={18} /> Back to Maintenance
        </button>
      </div>
    );
  }

  const tabs = [
    { key: 'overview', label: 'Overview', icon: <Layers size={16} /> },
    { key: 'documents', label: 'Documents', icon: <FileText size={16} /> },
    { key: 'maintenance', label: 'Maintenance', icon: <Settings size={16} /> },
    { key: 'failures', label: 'Failures', icon: <AlertTriangle size={16} /> },
  ];

  const specs = equipment.specifications || equipment.specs || {};
  const documents = equipment.related_documents || equipment.documents || [];
  const maintenanceRecords = equipment.maintenance_records || [];
  const failureEvents = equipment.failure_events || equipment.failures || [];

  const critColor = getCriticalityColor(equipment.criticality);

  return (
    <div className="equipment-detail-page animate-fade-in">
      <div className="page-header-row">
        <button className="btn btn-ghost" onClick={() => navigate('/maintenance')}>
          <ArrowLeft size={18} />
          Back to Maintenance
        </button>
      </div>

      <div className="equipment-header">
        <div className="equipment-header-icon" style={{ background: critColor + '22', color: critColor }}>
          <Wrench size={32} />
        </div>
        <div className="equipment-header-info">
          <div className="equipment-header-top">
            {equipment.tag && (
              <span className="equipment-tag">
                <Tag size={14} /> {equipment.tag}
              </span>
            )}
          </div>
          <h1 className="equipment-name">{equipment.name || equipment.equipment_name || 'Unnamed Equipment'}</h1>
          <div className="equipment-badges">
            {equipment.equipment_type && (
              <span className="badge badge-info">
                {EQUIPMENT_TYPE_LABELS[equipment.equipment_type] || capitalize(equipment.equipment_type)}
              </span>
            )}
            {equipment.criticality && (
              <span className="badge" style={{ background: critColor + '22', color: critColor, border: `1px solid ${critColor}44` }}>
                {capitalize(equipment.criticality)} Criticality
              </span>
            )}
            {equipment.status && (
              <span className={`badge ${getStatusBadgeClass(equipment.status)}`}>
                {EQUIPMENT_STATUS_LABELS[equipment.status] || capitalize(equipment.status)}
              </span>
            )}
          </div>
          {equipment.location && (
            <div className="equipment-location">
              <MapPin size={14} /> {equipment.location}
            </div>
          )}
        </div>
      </div>

      <div className="tabs-bar">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-content animate-fade-in">
        {activeTab === 'overview' && (
          <div className="equipment-overview">
            <div className="card">
              <div className="card-header">
                <h3>Equipment Information</h3>
              </div>
              <div className="card-body">
                <div className="equipment-specs-grid">
                  {equipment.manufacturer && (
                    <div className="spec-item">
                      <span className="spec-label">Manufacturer</span>
                      <span className="spec-value">{equipment.manufacturer}</span>
                    </div>
                  )}
                  {equipment.model && (
                    <div className="spec-item">
                      <span className="spec-label">Model</span>
                      <span className="spec-value">{equipment.model}</span>
                    </div>
                  )}
                  {equipment.serial_number && (
                    <div className="spec-item">
                      <span className="spec-label">Serial Number</span>
                      <span className="spec-value">{equipment.serial_number}</span>
                    </div>
                  )}
                  {equipment.install_date && (
                    <div className="spec-item">
                      <span className="spec-label">Installation Date</span>
                      <span className="spec-value">{formatDate(equipment.install_date)}</span>
                    </div>
                  )}
                  {equipment.last_maintenance && (
                    <div className="spec-item">
                      <span className="spec-label">Last Maintenance</span>
                      <span className="spec-value">{formatDate(equipment.last_maintenance)}</span>
                    </div>
                  )}
                  {equipment.next_maintenance && (
                    <div className="spec-item">
                      <span className="spec-label">Next Maintenance</span>
                      <span className="spec-value">{formatDate(equipment.next_maintenance)}</span>
                    </div>
                  )}
                  {equipment.operating_hours != null && (
                    <div className="spec-item">
                      <span className="spec-label">Operating Hours</span>
                      <span className="spec-value">{equipment.operating_hours.toLocaleString()} hrs</span>
                    </div>
                  )}
                  {equipment.risk_score != null && (
                    <div className="spec-item">
                      <span className="spec-label">Risk Score</span>
                      <span className="spec-value">{(equipment.risk_score * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {Object.keys(specs).length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3>Technical Specifications</h3>
                </div>
                <div className="card-body">
                  <div className="equipment-specs-grid">
                    {Object.entries(specs).map(([key, value]) => (
                      <div className="spec-item" key={key}>
                        <span className="spec-label">{capitalize(key.replace(/_/g, ' '))}</span>
                        <span className="spec-value">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {equipment.description && (
              <div className="card">
                <div className="card-header">
                  <h3>Description</h3>
                </div>
                <div className="card-body">
                  <p className="equipment-description">{equipment.description}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="equipment-documents">
            {documents.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} />
                <h3>No Related Documents</h3>
                <p>No documents have been linked to this equipment yet.</p>
              </div>
            ) : (
              <div className="documents-list">
                {documents.map((doc, idx) => (
                  <Link
                    to={`/documents/${doc.id || doc.document_id}`}
                    className="card document-card hoverable"
                    key={doc.id || doc.document_id || idx}
                  >
                    <div className="card-body document-card-body">
                      <FileText size={20} className="doc-icon" />
                      <div className="doc-info">
                        <h4>{doc.title || doc.name || 'Untitled Document'}</h4>
                        {doc.category && <span className="badge badge-secondary">{capitalize(doc.category)}</span>}
                        {doc.created_at && <span className="doc-date">{formatDate(doc.created_at)}</span>}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'maintenance' && (
          <div className="equipment-maintenance">
            {maintenanceRecords.length === 0 ? (
              <div className="empty-state">
                <Settings size={48} />
                <h3>No Maintenance Records</h3>
                <p>No maintenance history is available for this equipment.</p>
              </div>
            ) : (
              <FailureTimeline events={maintenanceRecords} />
            )}
          </div>
        )}

        {activeTab === 'failures' && (
          <div className="equipment-failures">
            {failureEvents.length === 0 ? (
              <div className="empty-state">
                <CheckCircle2 size={48} />
                <h3>No Failure Events</h3>
                <p>No failure events have been recorded for this equipment.</p>
              </div>
            ) : (
              <FailureTimeline events={failureEvents} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EquipmentDetailPage;
