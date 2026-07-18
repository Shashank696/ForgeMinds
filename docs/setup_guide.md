# ForgeMinds — Setup Guide

## Prerequisites

- **Docker Desktop** (v4.0+) — [Download](https://www.docker.com/products/docker-desktop/)
- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/)
- **Gemini API Key** (free) — [Get Key](https://aistudio.google.com/apikey)

## Step 1: Clone & Configure

```bash
git clone <repository-url>
cd forgeminds

# Copy and edit environment file
cp .env.example .env
# Edit .env — at minimum set GEMINI_API_KEY
```

## Step 2: Start Infrastructure (Docker)

```bash
# Start all database services
docker compose up -d postgres neo4j qdrant redis

# Verify services are running
docker compose ps

# Expected: all 4 services "running" / "healthy"
```

### Service Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | localhost:5432 | forgeminds / forgeminds_dev |
| Neo4j Browser | http://localhost:7474 | neo4j / forgeminds_dev |
| Qdrant Dashboard | http://localhost:6333/dashboard | — |
| Redis | localhost:6379 | — |

## Step 3: Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: Open http://localhost:8000/docs to see Swagger UI.

## Step 4: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Verify: Open http://localhost:5173 to see the app.

## Step 5: Seed Data (Optional)

```bash
# Activate venv first, then from project root:
python scripts/seed_db.py
```

## Common Issues

### Port Conflicts

If a port is already in use, stop the conflicting service or change the port in `docker-compose.yml` and `.env`.

### Docker Memory

Neo4j requires at least 1GB RAM. If Docker is memory-constrained:
```bash
# Increase Docker memory to 4GB+ in Docker Desktop settings
```

### Python Path

If `import shared` fails, ensure you're running from the project root:
```bash
# Correct — from project root
uvicorn backend.main:app --reload

# Incorrect — from backend/
cd backend
uvicorn main:app --reload  # shared imports will fail
```

### Tesseract Not Found

If OCR fails with "tesseract not found":
```bash
# Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH or set TESSERACT_CMD in .env

# Mac:
brew install tesseract

# Linux:
sudo apt-get install tesseract-ocr
```
