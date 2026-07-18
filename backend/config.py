"""
ForgeMinds — Application Configuration.
Loads environment variables from .env and exposes them via Settings.
"""

import sys
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────
    APP_ENV: str = "development"
    APP_NAME: str = "ForgeMinds"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173"

    # ─── PostgreSQL ──────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "forgeminds"
    POSTGRES_USER: str = "forgeminds"
    POSTGRES_PASSWORD: str = "forgeminds_dev"

    # ─── Neo4j ───────────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "forgeminds_dev"

    # ─── Qdrant ──────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # ─── Redis ───────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ─── LLM ─────────────────────────────────────────
    GEMINI_API_KEY: str = ""

    # ─── Authentication ──────────────────────────────
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440

    # ─── Storage ─────────────────────────────────────
    STORAGE_PATH: str = "./storage/documents"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings():
    return Settings()
