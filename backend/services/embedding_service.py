"""
ForgeMinds — Embedding Service.

Generates vector embeddings using sentence-transformers, stores them in
Qdrant via the QdrantClientWrapper, and provides similarity search.
Model loading is lazy and runs in a background thread to avoid blocking
the async event loop.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional

from backend.db.qdrant_client import vector_db
from backend.utils.logger import get_logger
from shared.constants import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    QDRANT_COLLECTION_NAME,
    SIMILARITY_THRESHOLD,
)

logger = get_logger(__name__)

# Deferred import — heavy dependency
SentenceTransformer = None  # populated on first use


def _lazy_import_st():
    """Import sentence_transformers only when needed."""
    global SentenceTransformer
    if SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as _ST
        SentenceTransformer = _ST


class EmbeddingService:
    """Generates and stores vector embeddings.

    Uses sentence-transformers for embedding generation and Qdrant for
    vector storage and retrieval.  The model is loaded lazily on first
    call and cached for the lifetime of the process.
    """

    def __init__(self) -> None:
        """Initialise with no model loaded."""
        self._model = None
        self._model_name: str = EMBEDDING_MODEL_NAME
        self._dimension: int = EMBEDDING_DIMENSION
        logger.info(
            "EmbeddingService created — model=%s dim=%d (lazy load)",
            self._model_name,
            self._dimension,
        )

    # ─── Model Management ────────────────────────────────

    async def _load_model(self) -> None:
        """Load the SentenceTransformer model in a background thread.

        This is called automatically on the first embedding request.
        Subsequent calls are no-ops.
        """
        if self._model is not None:
            return

        _lazy_import_st()

        def _load():
            logger.info("Loading embedding model '%s' …", self._model_name)
            return SentenceTransformer(self._model_name)

        self._model = await asyncio.to_thread(_load)
        logger.info("Embedding model '%s' loaded successfully", self._model_name)

    # ─── Embedding Generation ────────────────────────────

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a single embedding vector for the given text.

        Args:
            text: The input text string.

        Returns:
            A list of floats with length equal to EMBEDDING_DIMENSION.
        """
        await self._load_model()

        def _encode():
            return self._model.encode(text, show_progress_bar=False).tolist()

        vector = await asyncio.to_thread(_encode)
        return vector

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 64
    ) -> List[List[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of input strings.
            batch_size: Sentences per internal batch passed to the model.

        Returns:
            List of embedding vectors (one per input text).
        """
        if not texts:
            return []

        await self._load_model()

        def _encode_batch():
            return self._model.encode(
                texts, batch_size=batch_size, show_progress_bar=False
            ).tolist()

        vectors = await asyncio.to_thread(_encode_batch)
        logger.info("Generated embeddings for %d texts", len(texts))
        return vectors

    # ─── Chunk Embedding ─────────────────────────────────

    async def embed_chunks(
        self, document_id: str, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Embed document chunks and return enriched chunk dicts.

        Each chunk dict is expected to contain at minimum a ``chunk_text``
        key.  Additional metadata keys (``chunk_index``, ``page_number``,
        ``document_title``, ``document_category``, ``entities``) are
        preserved and passed through.

        Args:
            document_id: The parent document identifier.
            chunks: List of chunk dictionaries.

        Returns:
            The same chunk dicts with an ``embedding`` key added.
        """
        if not chunks:
            return []

        texts = [c.get("chunk_text", "") for c in chunks]
        vectors = await self.generate_embeddings_batch(texts)

        enriched: List[Dict[str, Any]] = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            enriched_chunk = {
                **chunk,
                "document_id": document_id,
                "chunk_index": chunk.get("chunk_index", idx),
                "embedding": vector,
            }
            enriched.append(enriched_chunk)

        logger.info(
            "Embedded %d chunks for document_id=%s", len(enriched), document_id
        )
        return enriched

    # ─── Storage ─────────────────────────────────────────

    async def store_embeddings(
        self, document_id: str, embedded_chunks: List[Dict[str, Any]]
    ) -> None:
        """Store embedded chunks in Qdrant.

        Each chunk becomes a Qdrant point with its embedding as the
        vector and metadata fields in the payload.

        Args:
            document_id: The parent document identifier.
            embedded_chunks: Chunk dicts containing ``embedding`` and
                metadata fields.
        """
        if not embedded_chunks:
            return

        from qdrant_client.models import PointStruct

        points: List[PointStruct] = []
        for chunk in embedded_chunks:
            point_id = str(uuid.uuid4())
            payload = {
                "document_id": chunk.get("document_id", document_id),
                "chunk_index": chunk.get("chunk_index", 0),
                "chunk_text": chunk.get("chunk_text", ""),
                "page_number": chunk.get("page_number"),
                "document_title": chunk.get("document_title", ""),
                "document_category": chunk.get("document_category", ""),
                "entities": chunk.get("entities", []),
            }
            points.append(
                PointStruct(
                    id=point_id,
                    vector=chunk["embedding"],
                    payload=payload,
                )
            )

        await vector_db.batch_upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points,
            batch_size=100,
        )
        logger.info(
            "Stored %d embedding points for document_id=%s",
            len(points),
            document_id,
        )

    # ─── Search ──────────────────────────────────────────

    async def search_similar(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Embed a query and search Qdrant for similar chunks.

        Args:
            query: The search query string.
            limit: Maximum number of results.
            filters: Optional dict of Qdrant filter conditions.

        Returns:
            List of result dicts with chunk metadata and relevance score.
        """
        query_vector = await self.generate_embedding(query)

        # Build optional Qdrant filter
        filter_obj = None
        if filters:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            must_conditions = []
            for key, value in filters.items():
                if value is not None:
                    must_conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            if must_conditions:
                filter_obj = Filter(must=must_conditions)

        scored_points = await vector_db.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            score_threshold=SIMILARITY_THRESHOLD,
            filter_conditions=filter_obj,
        )

        results: List[Dict[str, Any]] = []
        for point in scored_points:
            payload = point.payload or {}
            results.append(
                {
                    "document_id": payload.get("document_id", ""),
                    "chunk_text": payload.get("chunk_text", ""),
                    "chunk_index": payload.get("chunk_index", 0),
                    "page_number": payload.get("page_number"),
                    "document_title": payload.get("document_title", ""),
                    "document_category": payload.get("document_category", ""),
                    "entities": payload.get("entities", []),
                    "relevance_score": float(point.score),
                }
            )

        logger.info(
            "Similarity search returned %d results for query='%s'",
            len(results),
            query[:80],
        )
        return results

    # ─── Deletion ────────────────────────────────────────

    async def delete_document_embeddings(self, document_id: str) -> None:
        """Delete all embeddings for a specific document.

        Args:
            document_id: The document whose vectors should be removed.
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        filter_obj = Filter(
            must=[
                FieldCondition(
                    key="document_id", match=MatchValue(value=document_id)
                )
            ]
        )
        await vector_db.delete_by_filter(
            collection_name=QDRANT_COLLECTION_NAME,
            filter_conditions=filter_obj,
        )
        logger.info(
            "Deleted embeddings for document_id=%s", document_id
        )


# Module-level singleton
embedding_service = EmbeddingService()
