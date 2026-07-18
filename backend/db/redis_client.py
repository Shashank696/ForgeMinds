"""
ForgeMinds — Redis Client.
Handles async Redis caching operations.
"""

import redis.asyncio as aioredis
from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis async client wrapper."""

    def __init__(self):
        self._redis = None

    async def connect(self):
        """Initialize Redis connection."""
        if self._redis is not None:
            return

        settings = get_settings()
        try:
            logger.info("Connecting to Redis at %s:%d...", settings.REDIS_HOST, settings.REDIS_PORT)
            self._redis = await aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
                socket_timeout=5.0,
            )
            await self._redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as exc:
            logger.warning("Failed to connect to Redis (caching will be disabled): %s", exc)
            self._redis = None

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis is not None:
            logger.info("Disconnecting from Redis...")
            await self._redis.close()
            self._redis = None

    async def get(self, key: str) -> str:
        """Get value by key."""
        if self._redis is None:
            return None
        try:
            return await self._redis.get(key)
        except Exception as exc:
            logger.error("Redis GET error: %s", exc)
            return None

    async def set(self, key: str, value: str, expire: int = None):
        """Set key-value pair."""
        if self._redis is None:
            return
        try:
            await self._redis.set(key, value, ex=expire)
        except Exception as exc:
            logger.error("Redis SET error: %s", exc)

    async def delete(self, key: str):
        """Delete a key."""
        if self._redis is None:
            return
        try:
            await self._redis.delete(key)
        except Exception as exc:
            logger.error("Redis DEL error: %s", exc)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._redis is None:
            return False
        try:
            val = await self._redis.exists(key)
            return bool(val)
        except Exception as exc:
            logger.error("Redis EXISTS error: %s", exc)
            return False


cache = RedisClient()
