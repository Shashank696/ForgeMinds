# ForgeMinds — Industrial Knowledge Intelligence Platform

> *Where industrial knowledge forges itself into intelligence.*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![React](https://img.shields.io/badge/react-18-61DAFB.svg)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-009688.svg)]()

## Overview

ForgeMinds is an AI-powered platform that ingests heterogeneous industrial documents — engineering drawings, maintenance records, safety procedures, inspection reports, operating instructions — and transforms them into a **living, queryable, proactive knowledge brain**.

### Key Features

- 🔍 **Universal Document Ingestion** — PDFs, images, spreadsheets, scanned forms, drawings
- 🧠 **Knowledge Graph** — Structured relationships across equipment, procedures, regulations
- 💬 **Expert Copilot** — RAG-powered conversational AI with source citations
- ⚙️ **Maintenance Intelligence** — Predictive recommendations and RCA support
- ✅ **Compliance Intelligence** — Regulatory gap detection and audit evidence
- 📊 **Analytics Dashboard** — Operational visibility and system insights

## Team

| Member | Role |
|--------|------|
| **SP** | Chief Architect, Integrator, Documentation Lead |
| **Rudra** | Document Intelligence & Knowledge Graph |
| **Harsh** | AI Engine & Multi-Agent System |
| **Dil** | Frontend & User Experience |

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- Python 3.11+
- Node.js 18+
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd forgeminds

# Copy environment file
cp .env.example .env
# Edit .env with your Gemini API key (free: https://aistudio.google.com/apikey)

# Start all services
docker compose up -d

# Access the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
```

### Option 2: Local Development

#### 1. Start Infrastructure

```bash
# Start only databases
docker compose up -d postgres neo4j qdrant redis
```

#### 2. Backend

```bash
# Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations (auto-runs on first connect)

# Start server
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## Project Structure

```
forgeminds/
├── frontend/          # React + Vite (Dil)
├── backend/           # FastAPI (Rudra + Harsh)
│   ├── api/           # Route handlers
│   ├── services/      # Business logic
│   ├── db/            # Database clients
│   ├── models/        # Pydantic models (from shared/)
│   └── utils/         # Utilities
├── shared/            # 🔒 LOCKED contracts (SP only)
├── data/              # Sample & seed data
├── docs/              # Documentation
├── scripts/           # Utility scripts
└── tests/             # Test files
```

## Architecture

```
                    ┌─────────────┐
                    │  React SPA  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   FastAPI   │
                    │   Gateway   │
                    └──────┬──────┘
              ┌────────────┼────────────┐
        ┌─────▼─────┐ ┌───▼────┐ ┌─────▼─────┐
        │ Document   │ │  RAG   │ │  Agent    │
        │ Ingestion  │ │Pipeline│ │Orchestrator│
        └─────┬──────┘ └───┬────┘ └─────┬─────┘
              │            │            │
    ┌─────────┼────────────┼────────────┤
    │         │            │            │
┌───▼──┐ ┌───▼──┐    ┌────▼──┐   ┌─────▼──┐
│Postgr│ │Neo4j │    │Qdrant │   │ Redis  │
│  SQL  │ │(Graph)│   │(Vector)│  │(Cache) │
└──────┘ └──────┘    └───────┘   └────────┘
```

## Development Guide

See [docs/setup_guide.md](docs/setup_guide.md) for detailed setup instructions.

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

See [docs/api_reference.md](docs/api_reference.md) for API documentation.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Recharts, react-force-graph |
| Backend | FastAPI, Python 3.11+ |
| Primary DB | PostgreSQL 16 |
| Knowledge Graph | Neo4j 5 Community |
| Vector DB | Qdrant |
| Cache/Queue | Redis 7 |
| LLM | Gemini 2.0 Flash (free tier) |
| Embeddings | sentence-transformers (local) |
| OCR | Tesseract 5, pdfplumber |
| Deployment | Docker Compose |

## License

MIT — Built for the ETAI Hackathon 2025.
