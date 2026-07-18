# ForgeMinds — API Reference

> Auto-generated Swagger docs available at: http://localhost:8000/docs

## Base URL

```
http://localhost:8000/api
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require a Bearer token:

```
Authorization: Bearer <jwt_token>
```

---

## Auth Endpoints

### POST /api/auth/login
Login and receive JWT token.

**Request:**
```json
{ "email": "string", "password": "string" }
```

**Response (200):**
```json
{ "access_token": "string", "token_type": "bearer", "user": { ... } }
```

### POST /api/auth/register
Register a new user.

**Request:**
```json
{ "email": "string", "password": "string", "full_name": "string", "role": "viewer", "department": "string" }
```

**Response (201):** `UserResponse`

### GET /api/auth/me
Get current authenticated user.

**Response (200):** `UserResponse`

---

## Document Endpoints

### POST /api/documents/upload
Upload a document for processing.

**Request:** `multipart/form-data` — `file` (binary), `category` (string, optional)

**Response (201):** `DocumentUploadResponse`

### GET /api/documents
List documents with pagination and filters.

**Query Params:** `page`, `limit`, `category`, `status`, `search`

**Response (200):** `PaginatedResponse<DocumentResponse>`

### GET /api/documents/{document_id}
Get full document detail.

**Response (200):** `DocumentDetailResponse`

### DELETE /api/documents/{document_id}
Delete a document.

**Response (204):** No Content

### GET /api/documents/{document_id}/entities
Get entities extracted from a document.

**Response (200):** `{ "entities": [EntityBrief] }`

### GET /api/documents/{document_id}/status
Poll document processing status.

**Response (200):** `DocumentStatusResponse`

---

## Search Endpoint

### POST /api/search
Hybrid search across all documents.

**Request:**
```json
{ "query": "string", "search_type": "hybrid", "filters": { ... }, "limit": 10 }
```

**Response (200):** `SearchResponse`

---

## Chat Endpoints

### POST /api/chat
Send a message to the knowledge copilot.

**Request:**
```json
{ "message": "string", "session_id": "optional", "agent_type": "auto", "context_filters": { ... } }
```

**Response (200):** `ChatResponse`

### GET /api/chat/history/{session_id}
Get chat history for a session.

**Response (200):** `{ "messages": [ChatMessageResponse] }`

### GET /api/chat/sessions
List all chat sessions.

**Query Params:** `page`, `limit`

**Response (200):** `{ "sessions": [SessionBrief] }`

---

## Knowledge Graph Endpoints

### GET /api/knowledge-graph/nodes
List knowledge graph nodes.

**Query Params:** `entity_type`, `search`, `limit`

**Response (200):** `{ "nodes": [GraphNode] }`

### GET /api/knowledge-graph/nodes/{node_id}
Get a single node with connections.

**Response (200):** `GraphNode`

### GET /api/knowledge-graph/subgraph/{node_id}
Get subgraph around a node.

**Query Params:** `depth` (default: 2, max: 3)

**Response (200):** `SubgraphResponse`

### GET /api/knowledge-graph/stats
Get knowledge graph statistics.

**Response (200):** `KGStatsResponse`

---

## Equipment Endpoints

### GET /api/equipment
List equipment with filters.

**Query Params:** `type`, `status`, `criticality`, `search`, `page`, `limit`

**Response (200):** `PaginatedResponse<EquipmentResponse>`

### GET /api/equipment/{equipment_id}
Get full equipment detail (digital twin).

**Response (200):** `EquipmentDetailResponse`

### GET /api/equipment/{equipment_id}/maintenance-history
Get maintenance history for equipment.

**Response (200):** `{ "records": [...] }`

### GET /api/equipment/{equipment_id}/failure-history
Get failure history for equipment.

**Response (200):** `{ "events": [...] }`

---

## Maintenance Intelligence Endpoints

### GET /api/maintenance/predictions
Get predictive maintenance recommendations.

**Query Params:** `equipment_id`, `criticality`

**Response (200):** `{ "predictions": [MaintenancePrediction] }`

### POST /api/maintenance/rca
Request root cause analysis.

**Request:**
```json
{ "equipment_id": "string", "failure_description": "string", "failure_date": "date" }
```

**Response (200):** `RCAResponse`

### GET /api/maintenance/alerts
Get proactive alerts.

**Response (200):** `{ "alerts": [ProactiveAlert] }`

---

## Compliance Endpoints

### GET /api/compliance/status
Get overall compliance status.

**Response (200):** `ComplianceOverview`

### GET /api/compliance/gaps
Get identified compliance gaps.

**Response (200):** `{ "gaps": [ComplianceGap] }`

### POST /api/compliance/assess
Trigger compliance assessment.

**Request:**
```json
{ "regulation_code": "string", "equipment_ids": ["string"] }
```

**Response (200):** Assessment results.

### GET /api/compliance/evidence-package/{regulation_code}
Generate compliance evidence package.

**Response (200):** Evidence package.

---

## Analytics Endpoints

### GET /api/analytics/overview
Get analytics dashboard data.

**Response (200):** `AnalyticsOverview`

### GET /api/analytics/trends
Get trend data for a metric.

**Query Params:** `metric`, `period` ('7d', '30d', '90d')

**Response (200):** Time-series data.
