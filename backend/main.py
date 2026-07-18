from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.utils.logger import get_logger
from backend.utils.constants import APP_NAME, APP_DESCRIPTION, APP_VERSION

from backend.api import (
    auth, documents, search, chat, knowledge_graph,
    maintenance, compliance, analytics, equipment
)

from backend.db.database import db
from backend.db.neo4j_client import neo4j_db
from backend.db.qdrant_client import vector_db
from backend.db.redis_client import cache

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("ForgeMinds v%s starting up", APP_VERSION)
    await db.connect(settings.postgres_dsn)
    await neo4j_db.connect()
    await vector_db.connect()
    await cache.connect()
    logger.info("All database connections established")
    yield
    logger.info("ForgeMinds shutting down")
    await db.disconnect()
    await neo4j_db.disconnect()
    await vector_db.disconnect()
    await cache.disconnect()
    logger.info("All connections closed")


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(knowledge_graph.router)
app.include_router(maintenance.router)
app.include_router(compliance.router)
app.include_router(analytics.router)
app.include_router(equipment.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint returning application info."""
    return {
        "title": APP_NAME,
        "description": APP_DESCRIPTION,
        "version": APP_VERSION,
        "docs": "/docs",
    }
