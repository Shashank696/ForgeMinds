"""
ForgeMinds — Qdrant Vector Database Client Wrapper.

Provides async access to Qdrant for vector storage, similarity search,
and collection management. Uses the synchronous QdrantClient wrapped
with asyncio.to_thread() for non-blocking operations.
"""

import os
import asyncio
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PointIdsList,
    FilterSelector,
    ScoredPoint,
    CollectionInfo,
)

from backend.utils.logger import get_logger
from shared.constants import QDRANT_COLLECTION_NAME, EMBEDDING_DIMENSION

logger = get_logger(__name__)


class QdrantClientWrapper:
    """Async wrapper around the Qdrant synchronous client.

    Manages connection lifecycle, collection creation, point upsert/delete,
    and similarity search operations. All blocking calls are dispatched
    via asyncio.to_thread to keep the event loop responsive.
    """

    def __init__(self) -> None:
        """Initialize the wrapper with no active connection."""
        self._client: Optional[QdrantClient] = None
        self._host: str = os.getenv("QDRANT_HOST", "localhost")
        self._port: int = int(os.getenv("QDRANT_PORT", "6333"))

    async def connect(self) -> None:
        """Create QdrantClient and ensure the default collection exists.

        Reads QDRANT_HOST and QDRANT_PORT from environment variables.
        Creates the default document_chunks collection if it does not
        already exist.
        """
        try:
            self._client = QdrantClient(
                host=self._host,
                port=self._port,
                timeout=30,
            )
            logger.info(
                "Connected to Qdrant at %s:%s", self._host, self._port
            )
            await self.ensure_collection(
                QDRANT_COLLECTION_NAME, EMBEDDING_DIMENSION
            )
        except Exception as e:
            logger.error("Failed to connect to Qdrant: %s", e)
            self._client = None

    async def disconnect(self) -> None:
        """Close the Qdrant client connection."""
        if self._client is not None:
            try:
                await asyncio.to_thread(self._client.close)
                logger.info("Disconnected from Qdrant")
            except Exception as e:
                logger.error("Error disconnecting from Qdrant: %s", e)
            finally:
                self._client = None

    async def ensure_collection(
        self, collection_name: str, vector_size: int
    ) -> None:
        """Create a collection only if it does not already exist.

        Args:
            collection_name: Name of the Qdrant collection.
            vector_size: Dimensionality of the vectors to store.
        """
        if self._client is None:
            logger.warning("Qdrant client not connected; cannot ensure collection")
            return

        try:
            collections = await asyncio.to_thread(
                self._client.get_collections
            )
            existing_names = [c.name for c in collections.collections]

            if collection_name not in existing_names:
                await asyncio.to_thread(
                    self._client.create_collection,
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "Created Qdrant collection '%s' (dim=%d, cosine)",
                    collection_name,
                    vector_size,
                )
            else:
                logger.info(
                    "Qdrant collection '%s' already exists", collection_name
                )
        except Exception as e:
            logger.error(
                "Failed to ensure collection '%s': %s", collection_name, e
            )

    async def create_collection(
        self, collection_name: str, vector_size: int
    ) -> None:
        """Create a new collection (idempotent via ensure_collection).

        Args:
            collection_name: Name of the Qdrant collection.
            vector_size: Dimensionality of the vectors to store.
        """
        await self.ensure_collection(collection_name, vector_size)

    async def upsert_points(
        self, collection_name: str, points: List[PointStruct]
    ) -> None:
        """Upsert a list of points into a collection.

        Args:
            collection_name: Target collection name.
            points: List of qdrant_client.models.PointStruct objects.
        """
        if self._client is None:
            logger.warning("Qdrant client not connected; cannot upsert points")
            return

        try:
            await asyncio.to_thread(
                self._client.upsert,
                collection_name=collection_name,
                points=points,
            )
            logger.info(
                "Upserted %d points into '%s'", len(points), collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to upsert %d points into '%s': %s",
                len(points),
                collection_name,
                e,
            )

    async def batch_upsert(
        self,
        collection_name: str,
        points: List[PointStruct],
        batch_size: int = 100,
    ) -> None:
        """Upsert points in batches to avoid oversized requests.

        Args:
            collection_name: Target collection name.
            points: Full list of PointStruct objects.
            batch_size: Number of points per batch.
        """
        if not points:
            return

        total = len(points)
        for start in range(0, total, batch_size):
            batch = points[start : start + batch_size]
            await self.upsert_points(collection_name, batch)
            logger.info(
                "Batch upsert progress: %d/%d",
                min(start + batch_size, total),
                total,
            )

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Filter] = None,
    ) -> List[ScoredPoint]:
        """Perform similarity search on a collection.

        Args:
            collection_name: Collection to search.
            query_vector: Query embedding vector.
            limit: Maximum number of results to return.
            score_threshold: Minimum similarity score (optional).
            filter_conditions: Qdrant Filter object (optional).

        Returns:
            List of ScoredPoint results ordered by relevance.
        """
        if self._client is None:
            logger.warning("Qdrant client not connected; cannot search")
            return []

        try:
            results = await asyncio.to_thread(
                self._client.search,
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions,
            )
            logger.info(
                "Search in '%s' returned %d results",
                collection_name,
                len(results),
            )
            return results
        except Exception as e:
            logger.error("Search failed in '%s': %s", collection_name, e)
            return []

    async def search_with_filter(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        must_conditions: List[FieldCondition],
        must_not_conditions: Optional[List[FieldCondition]] = None,
    ) -> List[ScoredPoint]:
        """Similarity search with explicit must/must_not filter conditions.

        Args:
            collection_name: Collection to search.
            query_vector: Query embedding vector.
            limit: Maximum number of results.
            must_conditions: List of FieldCondition that must all match.
            must_not_conditions: List of FieldCondition that must not match.

        Returns:
            List of ScoredPoint results.
        """
        filter_obj = Filter(
            must=must_conditions,
            must_not=must_not_conditions or [],
        )
        return await self.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            filter_conditions=filter_obj,
        )

    async def delete_points(
        self, collection_name: str, point_ids: List[str]
    ) -> None:
        """Delete points by their IDs.

        Args:
            collection_name: Collection to delete from.
            point_ids: List of point IDs (strings) to delete.
        """
        if self._client is None:
            logger.warning("Qdrant client not connected; cannot delete points")
            return

        if not point_ids:
            return

        try:
            await asyncio.to_thread(
                self._client.delete,
                collection_name=collection_name,
                points_selector=PointIdsList(points=point_ids),
            )
            logger.info(
                "Deleted %d points from '%s'", len(point_ids), collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to delete points from '%s': %s", collection_name, e
            )

    async def delete_by_filter(
        self, collection_name: str, filter_conditions: Filter
    ) -> None:
        """Delete points matching a filter (e.g. all chunks for a document).

        Args:
            collection_name: Collection to delete from.
            filter_conditions: Qdrant Filter specifying which points to delete.
        """
        if self._client is None:
            logger.warning(
                "Qdrant client not connected; cannot delete by filter"
            )
            return

        try:
            await asyncio.to_thread(
                self._client.delete,
                collection_name=collection_name,
                points_selector=FilterSelector(filter=filter_conditions),
            )
            logger.info(
                "Deleted points by filter from '%s'", collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to delete by filter from '%s': %s",
                collection_name,
                e,
            )

    async def get_collection_info(
        self, collection_name: str
    ) -> Dict[str, Any]:
        """Retrieve information about a collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            Dictionary with collection metadata, or empty dict on error.
        """
        if self._client is None:
            logger.warning(
                "Qdrant client not connected; cannot get collection info"
            )
            return {}

        try:
            info: CollectionInfo = await asyncio.to_thread(
                self._client.get_collection, collection_name=collection_name
            )
            return {
                "status": str(info.status),
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "segments_count": len(info.segments) if info.segments else 0,
                "config": str(info.config),
            }
        except Exception as e:
            logger.error(
                "Failed to get info for collection '%s': %s",
                collection_name,
                e,
            )
            return {}

    async def health_check(self) -> bool:
        """Check if Qdrant is reachable and healthy.

        Returns:
            True if the Qdrant service is responsive, False otherwise.
        """
        if self._client is None:
            return False

        try:
            await asyncio.to_thread(self._client.get_collections)
            return True
        except Exception as e:
            logger.error("Qdrant health check failed: %s", e)
            return False

    async def count_points(self, collection_name: str) -> int:
        """Count the number of points in a collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            Number of points, or 0 on error.
        """
        if self._client is None:
            logger.warning(
                "Qdrant client not connected; cannot count points"
            )
            return 0

        try:
            result = await asyncio.to_thread(
                self._client.count, collection_name=collection_name
            )
            return result.count
        except Exception as e:
            logger.error(
                "Failed to count points in '%s': %s", collection_name, e
            )
            return 0


vector_db = QdrantClientWrapper()
