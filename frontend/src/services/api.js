import axios from 'axios';
import {
  mockDocuments, mockDocumentDetail, mockEquipment, mockEquipmentDetail,
  mockGraphNodes, mockGraphEdges, mockGraphStats,
  mockChatSessions, mockChatResponse,
  mockSearchResults, mockPredictions, mockAlerts, mockRCAResponse,
  mockComplianceOverview, mockComplianceGaps,
  mockAnalyticsOverview, mockTrendData,
} from './mockData';

const api = axios.create({
  baseURL: '/api',
});

// ─── Request Interceptor (Auth Token) ─────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Response Interceptor (401 redirect) ──────────────────
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Helper: call API, fallback to mock data on 501 or network error.
 */
const withMock = async (apiCall, mockData) => {
  try {
    const res = await apiCall();
    return res.data;
  } catch (e) {
    const status = e.response?.status;
    if (status === 501 || status === 404 || !e.response) {
      return typeof mockData === 'function' ? mockData() : mockData;
    }
    throw e;
  }
};

// ═══════════════════════════════════════════════════════
//  Auth
// ═══════════════════════════════════════════════════════
export const login = (data) => api.post('/auth/login', data);
export const register = (data) => api.post('/auth/register', data);
export const getMe = () => api.get('/auth/me');

// ═══════════════════════════════════════════════════════
//  Documents
// ═══════════════════════════════════════════════════════
export const uploadDocument = (formData, onProgress) => {
  return new Promise((resolve) => {
    // Simulate upload progress for the demo video
    let progress = 0;
    const interval = setInterval(() => {
      progress += 20;
      if (onProgress) onProgress({ loaded: progress, total: 100 });
      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          resolve({ data: { message: "Document uploaded successfully", id: "doc-999" } });
        }, 500);
      }
    }, 200);
  });
};

export const fetchDocuments = (params = {}) =>
  withMock(() => api.get('/documents', { params }), mockDocuments);

export const fetchDocument = (id) =>
  withMock(() => api.get(`/documents/${id}`), mockDocumentDetail);

export const deleteDocument = (id) => api.delete(`/documents/${id}`);

export const fetchDocumentEntities = (id) =>
  withMock(() => api.get(`/documents/${id}/entities`), mockDocumentDetail.entities);

export const fetchDocumentStatus = (id) =>
  withMock(() => api.get(`/documents/${id}/status`), { upload_status: 'completed', processing_stage: 'graph_linked', progress_percent: 100 });

// ═══════════════════════════════════════════════════════
//  Search
// ═══════════════════════════════════════════════════════
export const searchDocuments = (data) =>
  withMock(() => api.post('/search', data), mockSearchResults);

// ═══════════════════════════════════════════════════════
//  Chat
// ═══════════════════════════════════════════════════════
export const sendChatMessage = (data) =>
  withMock(() => api.post('/chat', data), () => {
    const query = (data.message || '').toLowerCase();
    
    // Default response (Maintenance for P-101)
    let response = { ...mockChatResponse };
    
    if (query.includes('compliance') || query.includes('oisd')) {
      response.response = 'Based on the OISD-154 guidelines, the compliance requirements are:\n\n1. **Quarterly Audits**: All high-criticality equipment must be audited quarterly.\n2. **Vibration Limits**: Centrifugal pumps must operate below 4.5 mm/s RMS.\n\nYour recent inspection of P-101 indicates a compliance violation. Please review the OISD guidelines and schedule immediate maintenance to restore compliance.';
      response.agent_type = 'compliance';
      response.citations = [
        { document_id: 'doc-005', document_title: 'OISD Guidelines 154', chunk_text: 'All high-criticality equipment must be audited quarterly. Centrifugal pumps must operate below 4.5 mm/s RMS.', page_number: 12, relevance_score: 0.98 }
      ];
      response.suggested_followups = ['Generate a compliance report', 'What is the penalty for OISD-154 violations?'];
    } else if (query.includes('compressor') || query.includes('c-301')) {
      response.response = 'Compressor C-301 is currently showing a **Critical Alert** for Valve Wear.\n\nAccording to the maintenance records and predictive models, the suction valve plate is at high risk of fatigue cracking. This matches a similar historical incident from November 2023.\n\n> **Immediate Action Required**: Please schedule a valve inspection within 14 days.';
      response.agent_type = 'rca';
      response.citations = [
        { document_id: 'doc-004', document_title: 'Compressor Failure Report', chunk_text: 'Compressor C-301 experienced catastrophic bearing failure on November 5, 2023.', page_number: 3, relevance_score: 0.87 }
      ];
      response.suggested_followups = ['Show me the RCA for C-301', 'Order replacement valves'];
    }
    
    return response;
  });

export const fetchChatHistory = (sessionId) =>
  withMock(() => api.get(`/chat/history/${sessionId}`), { messages: [] });

export const fetchChatSessions = (params = {}) =>
  withMock(() => api.get('/chat/sessions', { params }), { sessions: mockChatSessions });

// ═══════════════════════════════════════════════════════
//  Knowledge Graph
// ═══════════════════════════════════════════════════════
export const fetchGraphNodes = (params = {}) =>
  withMock(() => api.get('/knowledge-graph/nodes', { params }), { nodes: mockGraphNodes });

export const fetchGraphNode = (id) =>
  withMock(() => api.get(`/knowledge-graph/nodes/${id}`), mockGraphNodes[0]);

export const fetchSubgraph = (id, params = {}) =>
  withMock(() => api.get(`/knowledge-graph/subgraph/${id}`, { params }), { nodes: mockGraphNodes, edges: mockGraphEdges });

export const fetchGraphStats = () =>
  withMock(() => api.get('/knowledge-graph/stats'), mockGraphStats);

// ═══════════════════════════════════════════════════════
//  Equipment
// ═══════════════════════════════════════════════════════
export const fetchEquipment = (params = {}) =>
  withMock(() => api.get('/equipment', { params }), mockEquipment);

export const fetchEquipmentDetail = (id) =>
  withMock(() => api.get(`/equipment/${id}`), mockEquipmentDetail);

export const fetchEquipmentMaintenanceHistory = (id) =>
  withMock(() => api.get(`/equipment/${id}/maintenance-history`), { records: mockEquipmentDetail.maintenance_records });

export const fetchEquipmentFailureHistory = (id) =>
  withMock(() => api.get(`/equipment/${id}/failure-history`), { events: mockEquipmentDetail.failure_events });

// ═══════════════════════════════════════════════════════
//  Maintenance Intelligence
// ═══════════════════════════════════════════════════════
export const fetchMaintenancePredictions = (params = {}) =>
  withMock(() => api.get('/maintenance/predictions', { params }), { predictions: mockPredictions });

export const requestRCA = (data) =>
  withMock(() => api.post('/maintenance/rca', data), mockRCAResponse);

export const fetchMaintenanceAlerts = () =>
  withMock(() => api.get('/maintenance/alerts'), { alerts: mockAlerts });

// ═══════════════════════════════════════════════════════
//  Compliance
// ═══════════════════════════════════════════════════════
export const fetchComplianceStatus = () =>
  withMock(() => api.get('/compliance/status'), mockComplianceOverview);

export const fetchComplianceGaps = () =>
  withMock(() => api.get('/compliance/gaps'), { gaps: mockComplianceGaps });

export const assessCompliance = (data) =>
  withMock(() => api.post('/compliance/assess', data), { status: 'assessment_started' });

export const fetchEvidencePackage = (code) =>
  withMock(() => api.get(`/compliance/evidence-package/${code}`), { documents: [], generated_at: new Date().toISOString() });

// ═══════════════════════════════════════════════════════
//  Analytics
// ═══════════════════════════════════════════════════════
export const fetchAnalyticsOverview = () =>
  withMock(() => api.get('/analytics/overview'), mockAnalyticsOverview);

export const fetchAnalyticsTrends = (params = {}) =>
  withMock(() => api.get('/analytics/trends', { params }), mockTrendData);

// ═══════════════════════════════════════════════════════
//  Health
// ═══════════════════════════════════════════════════════
export const checkHealth = () =>
  withMock(() => api.get('/health'), { status: 'ok' });

export default api;
