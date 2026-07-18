export const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleString();
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatPercentage = (value) => {
  if (typeof value !== 'number') return '0.0%';
  return (value * 100).toFixed(1) + '%';
};

export const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'var(--color-success)';
  if (score >= 0.5) return 'var(--color-warning)';
  return 'var(--color-danger)';
};

export const getStatusColor = (status) => {
  switch(status) {
    case 'completed':
    case 'compliant':
      return 'var(--color-success)';
    case 'pending':
    case 'processing':
    case 'partial':
      return 'var(--color-warning)';
    case 'failed':
    case 'non_compliant':
      return 'var(--color-danger)';
    default:
      return 'var(--color-text-muted)';
  }
};

export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};
