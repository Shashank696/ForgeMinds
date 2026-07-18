# ForgeMinds — API Reference

> **Base URL:** `http://localhost:8000`  
> **Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
> **Alternative Docs:** `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

All protected endpoints require a JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <token>
```

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```
**Response:** `201 Created` — Returns user profile

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
**Response:** `200 OK` — Returns JWT token
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```
**Response:** `200 OK` — Returns user profile

---

## Documents

### Upload Document
```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
category: "inspection_report"
```
**Response:** `201 Created` — Returns document ID and processing status

### List Documents
```http
GET /api/documents?page=1&limit=20&category=inspection_report&status=completed&search=pump
Authorization: Bearer <token>
```
**Response:** `200 OK` — Paginated document list

### Get Document Details
```http
GET /api/documents/{document_id}
Authorization: Bearer <token>
```
**Response:** `200 OK` — Full document details with extracted entities

### Delete Document
```http
DELETE /api/documents/{document_id}
Authorization: Bearer <token>
```
**Response:** `204 No Content`

### Get Document Entities
```http
GET /api/documents/{document_id}/entities
Authorization: Bearer <token>
```
**Response:** `200 OK` — List of extracted entities

---

## Search

### Hybrid Search
```http
POST /api/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "bearing failures in pumps",
  "search_type": "hybrid",
  "limit": 10,
  "filters": {
    "category": "maintenance_record",
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```
**Response:** `200 OK` — Ranked search results with relevance scores

---

## AI Chat

### Send Message
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What maintenance is recommended for Pump P-101?",
  "session_id": "optional-session-uuid"
}
```
**Response:** `200 OK`
```json
{
  "response": "Based on inspection reports...",
  "agent_type": "maintenance",
  "confidence": 0.87,
  "citations": [
    {"document_id": "...", "title": "INS-2024-001", "relevance": 0.95}
  ],
  "session_id": "..."
}
```

### Get Chat History
```http
GET /api/chat/history/{session_id}
Authorization: Bearer <token>
```

### List Chat Sessions
```http
GET /api/chat/sessions?page=1&limit=10
Authorization: Bearer <token>
```

---

## Knowledge Graph

### Query Nodes
```http
GET /api/knowledge-graph/nodes?entity_type=equipment&search=P-101&limit=50
Authorization: Bearer <token>
```

### Get Node with Connections
```http
GET /api/knowledge-graph/nodes/{node_id}
Authorization: Bearer <token>
```

### Get Subgraph
```http
GET /api/knowledge-graph/subgraph/{node_id}?depth=2
Authorization: Bearer <token>
```

### Graph Statistics
```http
GET /api/knowledge-graph/stats
Authorization: Bearer <token>
```

---

## Maintenance

### Get Failure Predictions
```http
GET /api/maintenance/predictions?equipment_id=P-101&criticality=high
Authorization: Bearer <token>
```

### Run Root Cause Analysis
```http
POST /api/maintenance/rca
Authorization: Bearer <token>
Content-Type: application/json

{
  "equipment_id": "P-101",
  "failure_description": "Unusual vibration detected during operation"
}
```

### Get Proactive Alerts
```http
GET /api/maintenance/alerts
Authorization: Bearer <token>
```

---

## Compliance

### Get Compliance Overview
```http
GET /api/compliance/status
Authorization: Bearer <token>
```

### Detect Gaps
```http
GET /api/compliance/gaps
Authorization: Bearer <token>
```

### Run Assessment
```http
POST /api/compliance/assess
Authorization: Bearer <token>
Content-Type: application/json

{
  "regulation_code": "ASME_B31_3",
  "equipment_ids": ["P-101", "V-200"]
}
```

### Get Evidence Package
```http
GET /api/compliance/evidence-package/{regulation_code}
Authorization: Bearer <token>
```

---

## Analytics

### Dashboard Overview
```http
GET /api/analytics/overview
Authorization: Bearer <token>
```

### Trend Data
```http
GET /api/analytics/trends?metric=document_processing&period=30d
Authorization: Bearer <token>
```

---

## Equipment

### List Equipment
```http
GET /api/equipment?type=pump&status=active&criticality=high&page=1&limit=20
Authorization: Bearer <token>
```

### Get Equipment Details
```http
GET /api/equipment/{equipment_id}
Authorization: Bearer <token>
```

### Maintenance History
```http
GET /api/equipment/{equipment_id}/maintenance-history
Authorization: Bearer <token>
```

---

## Health Check

```http
GET /api/health
```
**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Error Responses

All errors follow a consistent format:
```json
{
  "detail": "Error description"
}
```

| Status Code | Meaning |
|------------|---------|
| `400` | Bad Request — Invalid input |
| `401` | Unauthorized — Missing or invalid token |
| `403` | Forbidden — Insufficient permissions |
| `404` | Not Found — Resource doesn't exist |
| `422` | Validation Error — Invalid request body |
| `500` | Internal Server Error |
