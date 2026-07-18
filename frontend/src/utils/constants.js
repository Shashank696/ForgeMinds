/**
 * ForgeMinds — Frontend Constants (aligned with shared/enums.py)
 */

// ─── Document Categories ──────────────────────────────────
export const DOCUMENT_CATEGORIES = {
  MAINTENANCE_RECORD: 'maintenance_record',
  OPERATING_PROCEDURE: 'operating_procedure',
  INSPECTION_REPORT: 'inspection_report',
  ENGINEERING_DRAWING: 'engineering_drawing',
  SAFETY_PROCEDURE: 'safety_procedure',
  REGULATORY: 'regulatory',
  OEM_MANUAL: 'oem_manual',
  INCIDENT_REPORT: 'incident_report',
  WORK_ORDER: 'work_order',
  OTHER: 'other',
};

export const DOCUMENT_CATEGORY_LABELS = {
  maintenance_record: 'Maintenance Record',
  operating_procedure: 'Operating Procedure',
  inspection_report: 'Inspection Report',
  engineering_drawing: 'Engineering Drawing',
  safety_procedure: 'Safety Procedure',
  regulatory: 'Regulatory',
  oem_manual: 'OEM Manual',
  incident_report: 'Incident Report',
  work_order: 'Work Order',
  other: 'Other',
};

// ─── Upload Status ────────────────────────────────────────
export const UPLOAD_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// ─── Processing Stages ────────────────────────────────────
export const PROCESSING_STAGES = {
  UPLOADED: 'uploaded',
  OCR_COMPLETE: 'ocr_complete',
  ENTITIES_EXTRACTED: 'entities_extracted',
  EMBEDDED: 'embedded',
  GRAPH_LINKED: 'graph_linked',
};

export const PROCESSING_STAGE_LABELS = {
  uploaded: 'Uploaded',
  ocr_complete: 'OCR Complete',
  entities_extracted: 'Entities Extracted',
  embedded: 'Embedded',
  graph_linked: 'Graph Linked',
};

// ─── Equipment Types ──────────────────────────────────────
export const EQUIPMENT_TYPES = {
  PUMP: 'pump',
  VALVE: 'valve',
  COMPRESSOR: 'compressor',
  VESSEL: 'vessel',
  HEAT_EXCHANGER: 'heat_exchanger',
  INSTRUMENT: 'instrument',
  MOTOR: 'motor',
  TANK: 'tank',
  PIPING: 'piping',
  OTHER: 'other',
};

export const EQUIPMENT_TYPE_LABELS = {
  pump: 'Pump',
  valve: 'Valve',
  compressor: 'Compressor',
  vessel: 'Vessel',
  heat_exchanger: 'Heat Exchanger',
  instrument: 'Instrument',
  motor: 'Motor',
  tank: 'Tank',
  piping: 'Piping',
  other: 'Other',
};

// ─── Criticality ──────────────────────────────────────────
export const CRITICALITY_LEVELS = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

// ─── Equipment Status ─────────────────────────────────────
export const EQUIPMENT_STATUSES = {
  OPERATIONAL: 'operational',
  UNDER_MAINTENANCE: 'under_maintenance',
  SHUTDOWN: 'shutdown',
  DECOMMISSIONED: 'decommissioned',
};

export const EQUIPMENT_STATUS_LABELS = {
  operational: 'Operational',
  under_maintenance: 'Under Maintenance',
  shutdown: 'Shutdown',
  decommissioned: 'Decommissioned',
};

// ─── Agent Types ──────────────────────────────────────────
export const AGENT_TYPES = {
  AUTO: 'auto',
  GENERAL: 'general',
  MAINTENANCE: 'maintenance',
  COMPLIANCE: 'compliance',
  RCA: 'rca',
  LESSONS_LEARNED: 'lessons_learned',
};

export const AGENT_TYPE_LABELS = {
  auto: 'Auto',
  general: 'General',
  maintenance: 'Maintenance',
  compliance: 'Compliance',
  rca: 'Root Cause Analysis',
  lessons_learned: 'Lessons Learned',
};

export const AGENT_TYPE_COLORS = {
  auto: '#6366f1',
  general: '#3b82f6',
  maintenance: '#f59e0b',
  compliance: '#22c55e',
  rca: '#ef4444',
  lessons_learned: '#8b5cf6',
};

// ─── Entity Types ─────────────────────────────────────────
export const ENTITY_TYPES = {
  EQUIPMENT: 'equipment',
  DOCUMENT: 'document',
  PERSON: 'person',
  PROCEDURE: 'procedure',
  REGULATION: 'regulation',
  FAILURE_EVENT: 'failure_event',
  MAINTENANCE_ACTION: 'maintenance_action',
  LOCATION: 'location',
  PARAMETER: 'parameter',
  PART: 'part',
};

export const ENTITY_TYPE_LABELS = {
  equipment: 'Equipment',
  document: 'Document',
  person: 'Person',
  procedure: 'Procedure',
  regulation: 'Regulation',
  failure_event: 'Failure Event',
  maintenance_action: 'Maintenance Action',
  location: 'Location',
  parameter: 'Parameter',
  part: 'Part',
};

export const ENTITY_TYPE_COLORS = {
  equipment: '#6366f1',
  document: '#3b82f6',
  person: '#f59e0b',
  procedure: '#22c55e',
  regulation: '#ef4444',
  failure_event: '#f97316',
  maintenance_action: '#06b6d4',
  location: '#8b5cf6',
  parameter: '#ec4899',
  part: '#14b8a6',
};

// ─── Compliance Status ────────────────────────────────────
export const COMPLIANCE_STATUSES = {
  COMPLIANT: 'compliant',
  NON_COMPLIANT: 'non_compliant',
  PARTIALLY_COMPLIANT: 'partially_compliant',
  UNKNOWN: 'unknown',
  NOT_APPLICABLE: 'not_applicable',
};

export const COMPLIANCE_STATUS_LABELS = {
  compliant: 'Compliant',
  non_compliant: 'Non-Compliant',
  partially_compliant: 'Partially Compliant',
  unknown: 'Unknown',
  not_applicable: 'N/A',
};

// ─── Risk Levels ──────────────────────────────────────────
export const RISK_LEVELS = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

// ─── User Roles ───────────────────────────────────────────
export const USER_ROLES = {
  ADMIN: 'admin',
  ENGINEER: 'engineer',
  OPERATOR: 'operator',
  COMPLIANCE_OFFICER: 'compliance_officer',
  VIEWER: 'viewer',
};

// ─── Search Types ─────────────────────────────────────────
export const SEARCH_TYPES = {
  SEMANTIC: 'semantic',
  KEYWORD: 'keyword',
  GRAPH: 'graph',
  HYBRID: 'hybrid',
};

export const SEARCH_TYPE_LABELS = {
  semantic: 'Semantic Search',
  keyword: 'Keyword Search',
  graph: 'Graph Search',
  hybrid: 'Hybrid Search',
};

// ─── App Constants ────────────────────────────────────────
export const APP_NAME = 'ForgeMinds';
export const APP_VERSION = '1.0.0';
export const MAX_FILE_SIZE_MB = 50;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const ALLOWED_FILE_EXTENSIONS = [
  '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif',
  '.xlsx', '.xls', '.csv',
  '.docx', '.doc', '.txt',
  '.pptx', '.ppt',
  '.eml', '.msg',
];

// ─── Navigation Items ─────────────────────────────────────
export const NAV_SECTIONS = [
  {
    label: 'Overview',
    items: [
      { path: '/', label: 'Dashboard', icon: 'LayoutDashboard' },
      { path: '/documents', label: 'Documents', icon: 'FileText' },
      { path: '/search', label: 'Search', icon: 'Search' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { path: '/chat', label: 'AI Copilot', icon: 'MessageSquare' },
      { path: '/knowledge-graph', label: 'Knowledge Graph', icon: 'GitBranch' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { path: '/maintenance', label: 'Maintenance', icon: 'Wrench' },
      { path: '/compliance', label: 'Compliance', icon: 'Shield' },
      { path: '/analytics', label: 'Analytics', icon: 'BarChart3' },
    ],
  },
];
