# Contributing to ForgeMinds

## Team & Module Ownership

| Developer | Module | Files Owned |
|-----------|--------|-------------|
| **SP** | Architecture, Integration, Shared Contracts | `shared/`, `backend/models/`, `backend/main.py`, `backend/config.py`, `docker-compose.yml`, `docs/` |
| **Rudra** | Document Intelligence & Knowledge Graph | `backend/services/document_service.py`, `ingestion_service.py`, `ocr_service.py`, `entity_extraction.py`, `knowledge_graph_service.py`, `backend/api/documents.py`, `knowledge_graph.py`, `equipment.py`, `backend/db/neo4j_client.py` |
| **Harsh** | AI Engine & Multi-Agent System | `backend/services/embedding_service.py`, `search_service.py`, `rag_service.py`, `agent_orchestrator.py`, `maintenance_agent.py`, `compliance_agent.py`, `rca_agent.py`, `lessons_agent.py`, `backend/api/chat.py`, `search.py`, `maintenance.py`, `compliance.py`, `backend/db/qdrant_client.py` |
| **Dil** | Frontend & User Experience | `frontend/` (entire directory) |

## Rules

### File Ownership
- **NEVER** modify files outside your assigned module.
- If you need a change in someone else's file, **request it from SP**.
- `shared/` is **LOCKED** — only SP can modify it.

### Branch Naming
```
feature/<your-name>/<description>
  feature/rudra/document-ingestion
  feature/harsh/rag-pipeline
  feature/dil/dashboard-ui

bugfix/<your-name>/<description>
```

### Commit Messages
```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Scope: ingestion, rag, ui, kg, auth, api, db

Examples:
  feat(ingestion): add OCR pipeline for scanned PDFs
  feat(rag): implement hybrid retrieval with graph context
  fix(api): handle missing document category gracefully
```

### Code Style

**Python:**
- Formatter: `black --line-length 100`
- Type hints on all function signatures
- Google-style docstrings on public functions

**JavaScript:**
- Formatter: Prettier (default settings)
- Functional components with hooks
- Named exports (default export only for pages)

### API Contracts
- All endpoints use models from `shared/interfaces.py`
- If you need a new field or model, request it from SP
- Never return raw dictionaries — always use Pydantic models

### Error Handling

**Backend:**
```python
raise HTTPException(
    status_code=404,
    detail={"code": "NOT_FOUND", "message": "Document not found", "details": {}}
)
```

**Frontend:**
```javascript
try {
  const response = await api.getDocument(id);
} catch (error) {
  toast.error(error.response?.data?.detail?.message || 'An error occurred');
}
```

### Testing
- Write tests for critical paths
- Test files go in `tests/`
- Run tests with: `pytest tests/`

## Conflict Resolution

1. If two developers need the same file → **STOP, contact SP**.
2. `shared/` conflicts → SP's version wins.
3. API response mismatches → Backend is source of truth, frontend adapts.
4. Database changes → New migration file, never edit existing ones.
