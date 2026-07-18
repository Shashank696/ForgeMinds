# ForgeMinds — Architecture Documentation

## System Overview

ForgeMinds is built on a modern, async-first microservices architecture designed for industrial-scale document intelligence.

## Architecture Diagram

![Architecture](images/architecture.jpg)

## Layered Architecture

### Presentation Layer (Frontend)
- **React 18** with Vite build system
- Premium dark theme with glassmorphism effects
- 14 interactive pages, 30+ reusable components
- Real-time state management via React hooks
- Force-directed graph visualization (react-force-graph)
- Charts and analytics (Recharts)

### API Layer (FastAPI)
- Async REST API with automatic OpenAPI documentation
- JWT-based authentication with bcrypt password hashing
- Request validation via Pydantic v2 models
- CORS middleware with configurable origins
- Lifespan-managed database connections

### Service Layer (Business Logic)
- **14 service modules** organized by domain responsibility
- Shared interfaces (Pydantic models) ensure type safety
- Agent orchestrator routes queries to specialized AI agents
- RAG pipeline assembles context from 3 retrieval sources

### Data Layer (Multi-Database)
| Database | Purpose | Client |
|----------|---------|--------|
| PostgreSQL | Relational data (users, documents, equipment) | asyncpg |
| Neo4j | Knowledge graph (entities, relationships) | neo4j-driver |
| Qdrant | Vector embeddings (semantic search) | qdrant-client |
| Redis | Caching (sessions, queries) | aioredis |

## AI Pipeline

![AI Pipeline](images/ai_pipeline.jpg)

### Multi-Agent System
```
User Query → Intent Classification → Agent Selection
                                         │
         ┌──────────┬──────────┬─────────┴──────────┐
         ▼          ▼          ▼                     ▼
    Maintenance  Compliance   RCA            Lessons Learned
      Agent       Agent      Agent               Agent
         │          │          │                     │
         └──────────┴──────────┴─────────────────────┘
                              │
                    Hybrid Context Retrieval
                   (Vector + Graph + Keyword)
                              │
                    Gemini LLM Generation
                              │
                  Response + Citations + Confidence
```

## Knowledge Graph

![Knowledge Graph](images/knowledge_graph.jpg)

### Entity-Relationship Model
```
(:Equipment)-[:MAINTAINED_BY]->(:Person)
(:Document)-[:MENTIONS]->(:Equipment)
(:Equipment)-[:COMPLIANT_WITH]->(:Regulation)
(:Equipment)-[:FAILED_ON]->(:FailureMode)
(:Document)-[:REFERENCES]->(:Regulation)
(:Equipment)-[:LOCATED_AT]->(:Location)
```

## Database Schema

![Database Architecture](images/database.jpg)

### PostgreSQL Tables
- `users` — Authentication and user management
- `documents` — Document metadata and processing status
- `document_chunks` — Text chunks for RAG retrieval
- `equipment` — Industrial equipment registry
- `work_orders` — Maintenance work orders
- `maintenance_records` — Historical maintenance data
- `compliance_records` — Regulatory compliance records
- `chat_history` — AI conversation logs
- `audit_logs` — System activity tracking
- `search_history` — Search query analytics

## Workflow

![Workflow](images/workflow.jpg)

## Security
- JWT tokens with configurable expiry (default: 24h)
- bcrypt password hashing with salt
- Auth dependency injection on all protected endpoints
- CORS protection with configurable origins
