"""
ForgeMinds — Neo4j Async Client Wrapper.
Provides connection management, query execution, and retry logic for Neo4j.
"""

import asyncio
from typing import Optional, List, Dict, Any

from neo4j import AsyncGraphDatabase
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    Neo4jError,
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2  # seconds


class Neo4jClient:
    """Neo4j async driver wrapper."""

    def __init__(self):
        self._driver = None
        self._connected: bool = False

    # ──────────────────────────────────────────────
    # Connection lifecycle
    # ──────────────────────────────────────────────

    async def connect(self) -> None:
        """Initialize Neo4j connection with retry logic."""
        from backend.config import get_settings
        settings = get_settings()

        last_error: Optional[Exception] = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    max_connection_pool_size=50,
                )
                # Verify connectivity
                await self._driver.verify_connectivity()
                self._connected = True
                logger.info(
                    "Neo4j connected to %s (attempt %d)",
                    settings.NEO4J_URI, attempt,
                )

                # Create indexes / constraints for common labels
                await self._setup_indexes()
                return
            except AuthError as exc:
                logger.error("Neo4j authentication failed: %s", exc)
                raise
            except (ServiceUnavailable, OSError) as exc:
                last_error = exc
                delay = _RETRY_BASE_DELAY ** attempt
                logger.warning(
                    "Neo4j connection attempt %d/%d failed: %s — retrying in %ds",
                    attempt, _MAX_RETRIES, exc, delay,
                )
                await asyncio.sleep(delay)

        logger.error("Neo4j connection failed after %d attempts", _MAX_RETRIES)
        # Allow the application to start even without Neo4j
        self._connected = False

    async def disconnect(self) -> None:
        """Close Neo4j connection."""
        if self._driver is not None:
            await self._driver.close()
            self._connected = False
            logger.info("Neo4j connection closed")

    # ──────────────────────────────────────────────
    # Query helpers
    # ──────────────────────────────────────────────

    async def run_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a read query and return results as list of dicts."""
        self._ensure_connected()
        try:
            async with self._driver.session() as session:
                result = await session.run(query, parameters or {})
                records = [record.data() async for record in result]
            logger.debug("Neo4j READ (%d records): %s", len(records), query[:120])
            return records
        except Neo4jError as exc:
            logger.error("Neo4j read query failed: %s | query: %s", exc, query[:200])
            raise

    async def run_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a write query and return results as list of dicts."""
        self._ensure_connected()
        try:
            async with self._driver.session() as session:
                result = await session.run(query, parameters or {})
                records = [record.data() async for record in result]
            logger.debug("Neo4j WRITE (%d records): %s", len(records), query[:120])
            return records
        except Neo4jError as exc:
            logger.error("Neo4j write query failed: %s | query: %s", exc, query[:200])
            raise

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────

    def _ensure_connected(self) -> None:
        """Raise RuntimeError if the client is not connected."""
        if not self._connected or self._driver is None:
            raise RuntimeError(
                "Neo4j client is not connected. Call connect() first."
            )

    async def _setup_indexes(self) -> None:
        """Create uniqueness constraints and indexes for common labels."""
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Equipment) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Equipment) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Document) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Person) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Regulation) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Regulation) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:FailureEvent) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:MaintenanceAction) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Location) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Parameter) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Part) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Procedure) ON (n.id)",
        ]
        for q in index_queries:
            try:
                await self.run_write_query(q)
            except Neo4jError:
                # Index may already exist — non-fatal
                pass
        logger.info("Neo4j indexes verified")


# Module-level singleton
neo4j_db = Neo4jClient()
