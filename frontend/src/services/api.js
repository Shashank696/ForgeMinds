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
export const uploadDocument = (formData, onProgress) =>
  api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  });

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
  withMock(() => api.post('/chat', data), mockChatResponse);

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
