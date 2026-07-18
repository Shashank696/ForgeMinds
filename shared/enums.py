"""
ForgeMinds — Shared Enums (Single Source of Truth).

LOCKED: Only SP may modify this file.
All enums used by backend APIs, services, and frontend constants must be defined here.
"""

from enum import Enum


# ─── Document ────────────────────────────────────────────


class DocumentCategory(str, Enum):
    """Category of an ingested industrial document."""
    MAINTENANCE_RECORD = "maintenance_record"
    OPERATING_PROCEDURE = "operating_procedure"
    INSPECTION_REPORT = "inspection_report"
    ENGINEERING_DRAWING = "engineering_drawing"
    SAFETY_PROCEDURE = "safety_procedure"
    REGULATORY = "regulatory"
    OEM_MANUAL = "oem_manual"
    INCIDENT_REPORT = "incident_report"
    WORK_ORDER = "work_order"
    OTHER = "other"


class UploadStatus(str, Enum):
    """Processing status of an uploaded document."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, Enum):
    """Granular processing stage within the ingestion pipeline."""
    UPLOADED = "uploaded"
    OCR_COMPLETE = "ocr_complete"
    ENTITIES_EXTRACTED = "entities_extracted"
    EMBEDDED = "embedded"
    GRAPH_LINKED = "graph_linked"


# ─── Equipment ───────────────────────────────────────────


class EquipmentType(str, Enum):
    """Type classification for industrial equipment."""
    PUMP = "pump"
    VALVE = "valve"
    COMPRESSOR = "compressor"
    VESSEL = "vessel"
    HEAT_EXCHANGER = "heat_exchanger"
    INSTRUMENT = "instrument"
    MOTOR = "motor"
    TANK = "tank"
    PIPING = "piping"
    OTHER = "other"


class Criticality(str, Enum):
    """Criticality level for equipment or alerts."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EquipmentStatus(str, Enum):
    """Current operational status of equipment."""
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    SHUTDOWN = "shutdown"
    DECOMMISSIONED = "decommissioned"


# ─── AI Agents ───────────────────────────────────────────


class AgentType(str, Enum):
    """Type of AI agent to handle a query."""
    AUTO = "auto"
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"
    RCA = "rca"
    LESSONS_LEARNED = "lessons_learned"


# ─── Knowledge Graph ────────────────────────────────────


class EntityType(str, Enum):
    """Type of entity in the knowledge graph."""
    EQUIPMENT = "equipment"
    DOCUMENT = "document"
    PERSON = "person"
    PROCEDURE = "procedure"
    REGULATION = "regulation"
    FAILURE_EVENT = "failure_event"
    MAINTENANCE_ACTION = "maintenance_action"
    LOCATION = "location"
    PARAMETER = "parameter"
    PART = "part"


# ─── Compliance ──────────────────────────────────────────


class ComplianceStatus(str, Enum):
    """Compliance assessment status for a regulation-equipment pair."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


# ─── Risk ────────────────────────────────────────────────


class RiskLevel(str, Enum):
    """Risk level for predictions and alerts."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ─── Users ───────────────────────────────────────────────


class UserRole(str, Enum):
    """User role for RBAC."""
    ADMIN = "admin"
    ENGINEER = "engineer"
    OPERATOR = "operator"
    COMPLIANCE_OFFICER = "compliance_officer"
    VIEWER = "viewer"


# ─── Work Orders ────────────────────────────────────────


class WorkOrderType(str, Enum):
    """Type of maintenance work order."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"


class WorkOrderStatus(str, Enum):
    """Status of a work order."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ─── Search ──────────────────────────────────────────────


class SearchType(str, Enum):
    """Search strategy type."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    GRAPH = "graph"
    HYBRID = "hybrid"
