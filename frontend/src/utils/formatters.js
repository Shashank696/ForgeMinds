/**
 * ForgeMinds — Formatting Utilities
 */

export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-IN', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
};

export const formatDateTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-IN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

export const formatRelativeTime = (date) => {
  if (!date) return '';
  const now = new Date();
  const d = new Date(date);
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHrs = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHrs / 24);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHrs < 24) return `${diffHrs}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(date);
};

export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export const formatPercentage = (value) => {
  if (typeof value !== 'number') return '0%';
  return (value * 100).toFixed(1) + '%';
};

export const formatScore = (value) => {
  if (typeof value !== 'number') return '—';
  return (value * 100).toFixed(0) + '%';
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text || '';
  return text.substring(0, maxLength) + '…';
};

export const capitalize = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};

export const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'var(--color-success)';
  if (score >= 0.5) return 'var(--color-warning)';
  return 'var(--color-danger)';
};

export const getConfidenceLabel = (score) => {
  if (score >= 0.8) return 'High';
  if (score >= 0.5) return 'Medium';
  return 'Low';
};

export const getStatusColor = (status) => {
  switch (status) {
    case 'completed': case 'compliant': case 'operational':
      return 'var(--color-success)';
    case 'pending': case 'processing': case 'partially_compliant': case 'under_maintenance':
      return 'var(--color-warning)';
    case 'failed': case 'non_compliant': case 'shutdown':
      return 'var(--color-danger)';
    default:
      return 'var(--color-text-muted)';
  }
};

export const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'completed': case 'compliant': case 'operational':
      return 'badge-success';
    case 'pending': case 'processing': case 'partially_compliant': case 'under_maintenance':
      return 'badge-warning';
    case 'failed': case 'non_compliant': case 'shutdown': case 'decommissioned':
      return 'badge-danger';
    default:
      return 'badge-secondary';
  }
};

export const getRiskColor = (level) => {
  switch (level) {
    case 'critical': return 'var(--color-danger)';
    case 'high': return '#f97316';
    case 'medium': return 'var(--color-warning)';
    case 'low': return 'var(--color-success)';
    default: return 'var(--color-text-muted)';
  }
};

export const getRiskBadgeClass = (level) => {
  switch (level) {
    case 'critical': return 'badge-danger';
    case 'high': return 'badge-warning';
    case 'medium': return 'badge-info';
    case 'low': return 'badge-success';
    default: return 'badge-secondary';
  }
};

export const getCriticalityColor = (level) => {
  switch (level) {
    case 'critical': return 'var(--color-danger)';
    case 'high': return '#f97316';
    case 'medium': return 'var(--color-warning)';
    case 'low': return 'var(--color-info)';
    default: return 'var(--color-text-muted)';
  }
};

export const getFileIcon = (fileType) => {
  if (!fileType) return 'FileText';
  const lower = fileType.toLowerCase();
  if (lower.includes('pdf')) return 'FileText';
  if (lower.includes('image') || lower.includes('png') || lower.includes('jpg')) return 'Image';
  if (lower.includes('spreadsheet') || lower.includes('xlsx') || lower.includes('csv')) return 'Sheet';
  if (lower.includes('doc')) return 'FileText';
  return 'File';
};

export const formatNumber = (num) => {
  if (typeof num !== 'number') return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toLocaleString();
};
