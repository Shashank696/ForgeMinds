import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (data) => api.post('/auth/login', data);
export const register = (data) => api.post('/auth/register', data);
export const getMe = () => api.get('/auth/me');

// Documents
export const uploadDocument = (data) => api.post('/documents', data);
export const getDocuments = () => api.get('/documents');
export const getDocument = (id) => api.get(`/documents/${id}`);
export const deleteDocument = (id) => api.delete(`/documents/${id}`);
export const getDocumentEntities = (id) => api.get(`/documents/${id}/entities`);
export const getDocumentStatus = (id) => api.get(`/documents/${id}/status`);

// Search
export const search = (query) => api.get('/search', { params: { q: query } });

// Chat
export const sendMessage = (data) => api.post('/chat', data);
export const getChatHistory = (sessionId) => api.get(`/chat/${sessionId}`);
export const getChatSessions = () => api.get('/chat/sessions');

// Knowledge Graph
export const getGraphNodes = () => api.get('/graph/nodes');
export const getGraphNode = (id) => api.get(`/graph/nodes/${id}`);
export const getSubgraph = (id) => api.get(`/graph/subgraph/${id}`);
export const getGraphStats = () => api.get('/graph/stats');

// Equipment
export const getEquipment = () => api.get('/equipment');
export const getEquipmentDetail = (id) => api.get(`/equipment/${id}`);
export const getEquipmentMaintenanceHistory = (id) => api.get(`/equipment/${id}/maintenance`);
export const getEquipmentFailureHistory = (id) => api.get(`/equipment/${id}/failures`);

// Maintenance
export const getMaintenancePredictions = () => api.get('/maintenance/predictions');
export const requestRCA = (data) => api.post('/maintenance/rca', data);
export const getMaintenanceAlerts = () => api.get('/maintenance/alerts');

// Compliance
export const getComplianceStatus = () => api.get('/compliance/status');
export const getComplianceGaps = () => api.get('/compliance/gaps');
export const assessCompliance = (data) => api.post('/compliance/assess', data);
export const getEvidencePackage = (id) => api.get(`/compliance/evidence/${id}`);

// Analytics
export const getAnalyticsOverview = () => api.get('/analytics/overview');
export const getAnalyticsTrends = () => api.get('/analytics/trends');

export default api;
