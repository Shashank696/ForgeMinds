# ForgeMinds — Architecture

## System Overview

ForgeMinds is a multi-tier application with the following layers:

1. **Client Layer** — React SPA (Progressive Web App)
2. **API Gateway** — FastAPI with JWT authentication
3. **Core Services** — Document ingestion, entity extraction, knowledge graph management
4. **AI Services** — RAG pipeline, multi-agent orchestration, specialized agents
5. **Data Layer** — PostgreSQL, Neo4j, Qdrant, Redis

## Data Flow

### Document Ingestion Pipeline

```
Upload → Type Detection → Text Extraction (OCR/pdfplumber)
    → Chunking → Entity Extraction → [Parallel]
        → Embedding Generation → Qdrant (Vector Store)
        → Knowledge Graph Update → Neo4j (Graph DB)
    → Metadata Storage → PostgreSQL
```

### Query Processing Pipeline

```
User Query → Intent Classification → Agent Routing
    → [Parallel Retrieval]
        → Vector Search (Qdrant)
        → Graph Traversal (Neo4j)
        → Keyword Search (PostgreSQL)
    → Context Fusion & Re-ranking
    → Specialized Agent Processing
    → Response Generation with Citations
```

## Component Responsibilities

### Document Intelligence (Rudra)
- File upload and storage
- OCR pipeline (Tesseract + pdfplumber)
- Text chunking with semantic awareness
- Entity extraction (equipment tags, dates, regulations, personnel)
- Knowledge graph CRUD (Neo4j)
- Document and equipment APIs

### AI Engine (Harsh)
- Embedding generation (sentence-transformers)
- Hybrid search (vector + keyword + graph)
- RAG pipeline (retrieve → re-rank → generate)
- Agent orchestrator (intent → route → aggregate)
- Specialized agents: Maintenance, Compliance, RCA, Lessons Learned
- Chat session management

### Frontend (Dil)
- React SPA with dark-theme design system
- Dashboard with system statistics
- Document management (upload, browse, view)
- Knowledge Copilot (chat with citations)
- Knowledge Graph explorer (interactive visualization)
- Maintenance & Compliance dashboards
- Analytics views

## Database Architecture

| Database | Purpose | Key Data |
|----------|---------|----------|
| **PostgreSQL** | Primary relational store | Users, documents, equipment, work orders, chat history |
| **Neo4j** | Knowledge graph | Entities, relationships, graph traversals |
| **Qdrant** | Vector similarity search | Document chunk embeddings |
| **Redis** | Cache and queue | LLM response cache, session data, task queue |

## Security

- JWT-based authentication with role-based access control
- File upload validation (type, size)
- Parameterized queries (SQLAlchemy)
- CORS restricted to frontend origin
- Environment-based secrets management
