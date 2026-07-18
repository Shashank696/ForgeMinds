"""
ForgeMinds — Shared Interfaces / Pydantic Models (Single Source of Truth).

LOCKED: Only SP may modify this file.
All API request/response bodies MUST conform to these models.
All inter-service function signatures MUST use these models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from shared.enums import (
    DocumentCategory, UploadStatus, ProcessingStage,
    EquipmentType, Criticality, EquipmentStatus,
    AgentType, EntityType, ComplianceStatus, RiskLevel,
    UserRole, SearchType,
)


# ═══════════════════════════════════════════════════════
#  Atomic / Reusable Models
# ═══════════════════════════════════════════════════════


class Citation(BaseModel):
    """A reference back to a source document chunk."""
    document_id: str
    document_title: str
    chunk_text: str
    page_number: Optional[int] = None
    relevance_score: float = Field(ge=0.0, le=1.0)


class EntityBrief(BaseModel):
    """Minimal representation of a knowledge-graph entity."""
    id: str
    entity_type: EntityType
    name: str
    properties: Dict[str, Any] = {}


class EquipmentBrief(BaseModel):
    """Minimal representation of an equipment record."""
    id: str
    tag: str
    name: str
    equipment_type: EquipmentType
    criticality: Criticality


class IncidentBrief(BaseModel):
    """Minimal representation of a historical incident."""
    id: str
    description: str
    date: date
    equipment_tag: str
    severity: str


# ═══════════════════════════════════════════════════════
#  User Models
# ═══════════════════════════════════════════════════════


class UserCreate(BaseModel):
    """Request body for user registration."""
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None


class UserLogin(BaseModel):
    """Request body for login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Public user representation (never includes password)."""
    id: str
    email: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token returned after login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ═══════════════════════════════════════════════════════
#  Document Models
# ═══════════════════════════════════════════════════════


class DocumentUploadResponse(BaseModel):
    """Returned immediately after file upload."""
    id: str
    filename: str
    file_type: str
    document_category: Optional[str] = None
    upload_status: str = "processing"
    created_at: datetime


class DocumentResponse(BaseModel):
    """Standard document list item."""
    id: str
    filename: str
    original_filename: str
    file_type: str
    document_category: Optional[DocumentCategory] = None
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    upload_status: UploadStatus
    processing_stage: Optional[ProcessingStage] = None
    entity_count: int = 0
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """Full document detail (single-document view)."""
    extracted_text: Optional[str] = None
    metadata: Dict[str, Any] = {}
    entities: List[EntityBrief] = []
    linked_equipment: List[EquipmentBrief] = []
    chunk_count: int = 0


class DocumentStatusResponse(BaseModel):
    """Polling endpoint for upload progress."""
    upload_status: UploadStatus
    processing_stage: Optional[ProcessingStage] = None
    progress_percent: int = 0


# ═══════════════════════════════════════════════════════
#  Equipment Models
# ═══════════════════════════════════════════════════════


class EquipmentResponse(BaseModel):
    """Standard equipment list item."""
    id: str
    tag: str
    name: str
    equipment_type: EquipmentType
    description: Optional[str] = None
    location: Optional[str] = None
    plant: Optional[str] = None
    unit: Optional[str] = None
    criticality: Criticality
    status: EquipmentStatus
    manufacturer: Optional[str] = None


class EquipmentDetailResponse(EquipmentResponse):
    """Full equipment detail with related data."""
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    specifications: Dict[str, Any] = {}
    related_documents: List[DocumentResponse] = []
    maintenance_records: List[Dict[str, Any]] = []
    failure_events: List[Dict[str, Any]] = []
    compliance_records: List[Dict[str, Any]] = []


# ═══════════════════════════════════════════════════════
#  Knowledge Graph Models
# ═══════════════════════════════════════════════════════


class GraphNode(BaseModel):
    """A node in the knowledge graph visualization."""
    id: str
    entity_type: EntityType
    name: str
    properties: Dict[str, Any] = {}
    connection_count: int = 0


class GraphEdge(BaseModel):
    """An edge (relationship) in the knowledge graph."""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = {}
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class SubgraphResponse(BaseModel):
    """A subgraph around a focal node."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class KGStatsResponse(BaseModel):
    """Aggregate statistics for the knowledge graph."""
    total_nodes: int
    total_edges: int
    nodes_by_type: Dict[str, int]
    edges_by_type: Dict[str, int]


# ═══════════════════════════════════════════════════════
#  Chat / RAG Models
# ═══════════════════════════════════════════════════════


class ChatRequest(BaseModel):
    """Request body for the copilot chat endpoint."""
    message: str
    session_id: Optional[str] = None
    agent_type: AgentType = AgentType.AUTO
    context_filters: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from the copilot chat endpoint."""
    session_id: str
    response: str
    agent_type: AgentType
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: List[Citation] = []
    related_entities: List[EntityBrief] = []
    suggested_followups: List[str] = []
    metadata: Dict[str, Any] = {}


class ChatMessageResponse(BaseModel):
    """A single message in chat history."""
    id: str
    role: str   # 'user' | 'assistant'
    message: str
    agent_type: Optional[AgentType] = None
    citations: List[Citation] = []
    confidence_score: Optional[float] = None
    created_at: datetime


class SessionBrief(BaseModel):
    """Minimal representation of a chat session."""
    session_id: str
    title: Optional[str] = None
    message_count: int = 0
    last_message_at: datetime
    agent_type: Optional[AgentType] = None


# ═══════════════════════════════════════════════════════
#  Search Models
# ═══════════════════════════════════════════════════════


class SearchRequest(BaseModel):
    """Request body for the search endpoint."""
    query: str
    search_type: SearchType = SearchType.HYBRID
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(default=10, le=50)


class SearchResultItem(BaseModel):
    """A single search result."""
    document_id: str
    chunk_text: str
    relevance_score: float
    document_title: str
    document_category: Optional[str] = None
    page_number: Optional[int] = None
    highlights: List[str] = []
    entities: List[EntityBrief] = []


class SearchResponse(BaseModel):
    """Full search response with timing."""
    results: List[SearchResultItem]
    total_results: int
    search_time_ms: int


# ═══════════════════════════════════════════════════════
#  Maintenance Intelligence Models
# ═══════════════════════════════════════════════════════


class MaintenancePrediction(BaseModel):
    """A predictive maintenance recommendation."""
    equipment_id: str
    equipment_tag: str
    prediction_type: str
    risk_level: RiskLevel
    predicted_failure_mode: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    recommended_action: str
    supporting_evidence: List[Citation] = []
    estimated_date: Optional[date] = None


class RCARequest(BaseModel):
    """Request body for root cause analysis."""
    equipment_id: str
    failure_description: str
    failure_date: Optional[date] = None


class RootCause(BaseModel):
    """A single identified root cause."""
    cause: str
    confidence: float
    evidence: List[Citation] = []
    similar_incidents: List[IncidentBrief] = []


class RCAResponse(BaseModel):
    """Full RCA analysis response."""
    root_causes: List[RootCause]
    recommended_actions: List[str] = []
    related_equipment_at_risk: List[EquipmentBrief] = []


class ProactiveAlert(BaseModel):
    """A proactive warning pushed by the system."""
    id: str
    alert_type: str   # 'failure_pattern' | 'compliance_due' | 'maintenance_overdue'
    severity: RiskLevel
    title: str
    description: str
    equipment: Optional[EquipmentBrief] = None
    evidence: List[Citation] = []
    created_at: datetime


# ═══════════════════════════════════════════════════════
#  Compliance Models
# ═══════════════════════════════════════════════════════


class ComplianceOverview(BaseModel):
    """High-level compliance posture."""
    overall_compliance_score: float
    by_regulation: List[Dict[str, Any]]


class ComplianceGap(BaseModel):
    """A detected compliance gap."""
    id: str
    regulation_code: str
    regulation_name: str
    requirement_text: str
    compliance_status: ComplianceStatus
    gap_description: Optional[str] = None
    remediation_action: Optional[str] = None
    affected_equipment: List[EquipmentBrief] = []
    due_date: Optional[date] = None


class ComplianceAssessRequest(BaseModel):
    """Request body for compliance assessment."""
    regulation_code: str
    equipment_ids: List[str] = []


# ═══════════════════════════════════════════════════════
#  Analytics Models
# ═══════════════════════════════════════════════════════


class AnalyticsOverview(BaseModel):
    """Dashboard analytics summary."""
    total_documents: int
    total_entities: int
    total_equipment: int
    total_queries: int
    avg_response_time_ms: int
    documents_by_category: Dict[str, int]
    entities_by_type: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# ═══════════════════════════════════════════════════════
#  Generic Pagination Wrapper
# ═══════════════════════════════════════════════════════


class PaginatedResponse(BaseModel):
    """Generic wrapper for paginated list endpoints."""
    items: List[Any]
    total: int
    page: int
    limit: int


# ═══════════════════════════════════════════════════════
#  Error Response
# ═══════════════════════════════════════════════════════


class ErrorDetail(BaseModel):
    """Structured error detail."""
    code: str
    message: str
    details: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    error: ErrorDetail
