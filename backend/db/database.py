"""
ForgeMinds — PostgreSQL Async Client.
Manages connection pooling and query execution using asyncpg.
"""

import asyncpg
from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PostgresClient:
    """Async PostgreSQL connection manager."""

    def __init__(self):
        self._pool = None

    async def connect(self, dsn: str = None):
        """Initialize connection pool using settings if dsn is not provided."""
        if self._pool is not None:
            return

        settings = get_settings()
        connection_dsn = dsn or settings.postgres_dsn
        try:
            logger.info("Connecting to PostgreSQL database...")
            self._pool = await asyncpg.create_pool(
                dsn=connection_dsn,
                min_size=5,
                max_size=20,
                command_timeout=30.0,
            )
            logger.info("PostgreSQL connection pool initialized successfully.")
        except Exception as exc:
            logger.critical("Failed to connect to PostgreSQL: %s", exc)
            raise

    async def disconnect(self):
        """Close connection pool."""
        if self._pool is not None:
            logger.info("Closing PostgreSQL connection pool...")
            await self._pool.close()
            self._pool = None
            logger.info("PostgreSQL connection pool closed.")

    async def get_pool(self) -> asyncpg.Pool:
        """Return the connection pool."""
        if self._pool is None:
            await self.connect()
        return self._pool

    async def execute(self, query: str, *args) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch_one(self, query: str, *args) -> dict:
        """Fetch a single record."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_all(self, query: str, *args) -> list:
        """Fetch multiple records."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]


db = PostgresClient()
