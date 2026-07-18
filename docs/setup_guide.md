# ForgeMinds — Deployment Guide

## Cloud Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Vercel/        │────▶│   Render/        │
│   Netlify        │     │   Railway        │
│   (Frontend)     │     │   (Backend API)  │
└─────────────────┘     └───────┬─────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │   Neon    │ │  Neo4j   │ │  Qdrant  │
            │ Postgres  │ │  Aura    │ │  Cloud   │
            └──────────┘ └──────────┘ └──────────┘
                                           ▲
                                    ┌──────┘
                              ┌──────────┐
                              │  Redis   │
                              │  Cloud   │
                              └──────────┘
```

---

## Option A: Frontend on Vercel

### Steps

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Environment Variables** in Vercel Dashboard:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

### Alternative: Netlify

```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

---

## Option B: Backend on Render

### Steps

1. **Create a new Web Service** on [render.com](https://render.com)

2. **Connect GitHub repository** → Select `Shashank696/ForgeMinds`

3. **Build Settings:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version:** 3.11

4. **Environment Variables:** (Set all from `.env.example`)

### Alternative: Railway

```bash
railway login
railway init
railway up
```

---

## Database Setup

### Neon PostgreSQL (Free Tier)

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project: `forgeminds`
3. Copy the connection string
4. Run migrations:
   ```bash
   psql $DATABASE_URL < backend/db/migrations/001_initial.sql
   ```

### Neo4j Aura (Free Tier)

1. Sign up at [neo4j.com/aura](https://neo4j.com/cloud/aura-free/)
2. Create a free instance
3. Note the connection URI and password
4. Set `NEO4J_URI` and `NEO4J_PASSWORD` in environment

### Qdrant Cloud (Free Tier)

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free cluster
3. Note the URL and API key
4. Set `QDRANT_HOST` and `QDRANT_PORT` in environment

### Redis Cloud (Free Tier)

1. Sign up at [redis.com/try-free](https://redis.com/try-free/)
2. Create a free database
3. Note the host, port, and password
4. Set `REDIS_HOST`, `REDIS_PORT` in environment

---

## Environment Variables for Production

```bash
# Application
APP_ENV=production
CORS_ORIGINS=https://forgeminds.vercel.app

# PostgreSQL (Neon)
POSTGRES_HOST=ep-xxx.us-east-2.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=forgeminds
POSTGRES_USER=forgeminds
POSTGRES_PASSWORD=<your-neon-password>

# Neo4j (Aura)
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-aura-password>

# Qdrant (Cloud)
QDRANT_HOST=xxx.aws.cloud.qdrant.io
QDRANT_PORT=6333

# Redis (Cloud)
REDIS_HOST=redis-xxx.c1.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=12345

# Gemini
GEMINI_API_KEY=<your-gemini-api-key>

# Auth
JWT_SECRET_KEY=<generate-a-strong-random-string>
```

---

## Verification Checklist

- [ ] Frontend loads at production URL
- [ ] Backend `/api/health` returns `{"status": "healthy"}`
- [ ] API docs accessible at `/docs`
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] Document upload processes correctly
- [ ] AI chat returns responses
- [ ] Knowledge graph queries return data
- [ ] Search returns relevant results
