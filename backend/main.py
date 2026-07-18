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

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: configurable origins
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

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    await db.connect("TODO: DSN")
    await neo4j_db.connect()
    await vector_db.connect()
    await cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    await db.disconnect()
    await neo4j_db.disconnect()
    await vector_db.disconnect()
    await cache.disconnect()

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "title": APP_NAME,
        "description": APP_DESCRIPTION,
        "version": APP_VERSION
    }
