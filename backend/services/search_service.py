"""
ForgeMinds — Search Service.

Orchestrates hybrid search across three backends:
  - Qdrant (semantic / vector similarity)
  - PostgreSQL (keyword / full-text)
  - Neo4j (graph traversal)

Results are combined using Reciprocal Rank Fusion (RRF) for a unified
relevance ranking.
"""

import asyncio
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.db.neo4j_client import neo4j_db
from backend.services.embedding_service import embedding_service
from backend.utils.logger import get_logger
from shared.constants import DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT
from shared.interfaces import EntityBrief, SearchResultItem

logger = get_logger(__name__)

# RRF constant (standard value from the literature)
_RRF_K = 60


class SearchService:
    """Orchestrates search across vector, keyword, and graph sources.

    Each individual search method can be invoked independently, or
    hybrid_search can be used to combine all three via Reciprocal Rank
    Fusion.
    """

    def __init__(self) -> None:
        """Initialise with references to embedding service and DB clients."""
        self._embedding = embedding_service
        self._db = db
        self._neo4j = neo4j_db
        logger.info("SearchService initialised")

    # ─── Semantic Search ─────────────────────────────────

    async def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[SearchResultItem]:
        """Pure vector similarity search via Qdrant.

        Args:
            query: The search query string.
            filters: Optional metadata filter dict.
            limit: Maximum number of results.

        Returns:
            List of SearchResultItem ordered by vector similarity.
        """
        try:
            raw_results = await self._embedding.search_similar(
                query=query, limit=min(limit, MAX_SEARCH_LIMIT), filters=filters
            )
            items = [self._build_search_result_item(r) for r in raw_results]
            logger.info("Semantic search returned %d results", len(items))
            return items
        except Exception as exc:
            logger.error("Semantic search failed: %s", exc)
            return []

    # ─── Keyword Search ──────────────────────────────────

    async def keyword_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[SearchResultItem]:
        """Full-text keyword search against PostgreSQL.

        Uses ILIKE matching on document_chunks.chunk_text and
        documents.extracted_text.  Falls back to empty results when the
        database is not connected or tables do not exist.

        Args:
            query: The search query string.
            filters: Optional metadata filter dict.
            limit: Maximum number of results.

        Returns:
            List of SearchResultItem ordered by keyword relevance.
        """
        try:
            # Build search pattern
            search_pattern = f"%{query}%"

            sql = """
                SELECT
                    dc.document_id,
                    dc.chunk_text,
                    dc.chunk_index,
                    dc.page_number,
                    d.original_filename AS document_title,
                    d.document_category
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id::text
                WHERE dc.chunk_text ILIKE $1
            """
            params: list = [search_pattern]

            # Apply optional category filter
            if filters and filters.get("document_category"):
                sql += " AND d.document_category = $2"
                params.append(filters["document_category"])

            sql += f" LIMIT {min(limit, MAX_SEARCH_LIMIT)}"

            rows = await self._db.fetch_all(sql, *params)

            if not rows:
                logger.info("Keyword search returned 0 results (or DB not ready)")
                return []

            items: List[SearchResultItem] = []
            for idx, row in enumerate(rows):
                # Simple relevance scoring — exact matches scored higher
                query_lower = query.lower()
                chunk_text = row.get("chunk_text", "") if isinstance(row, dict) else ""
                if query_lower in chunk_text.lower():
                    score = 0.8 - (idx * 0.02)
                else:
                    score = 0.5 - (idx * 0.02)
                score = max(score, 0.1)

                r = row if isinstance(row, dict) else dict(row) if row else {}
                items.append(
                    SearchResultItem(
                        document_id=r.get("document_id", ""),
                        chunk_text=r.get("chunk_text", ""),
                        relevance_score=score,
                        document_title=r.get("document_title", "Unknown"),
                        document_category=r.get("document_category"),
                        page_number=r.get("page_number"),
                        highlights=self._extract_highlights(
                            r.get("chunk_text", ""), query
                        ),
                        entities=[],
                    )
                )

            logger.info("Keyword search returned %d results", len(items))
            return items

        except Exception as exc:
            logger.warning("Keyword search failed (DB may be unavailable): %s", exc)
            return []

    # ─── Graph Search ────────────────────────────────────

    async def graph_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[SearchResultItem]:
        """Search the Neo4j knowledge graph for relevant entities and
        retrieve their associated document chunks.

        Args:
            query: The search query string.
            filters: Optional metadata filter dict.
            limit: Maximum number of results.

        Returns:
            List of SearchResultItem from graph-linked documents.
        """
        try:
            # Search for matching entities in Neo4j
            cypher = """
                MATCH (e)
                WHERE toLower(e.name) CONTAINS toLower($query)
                   OR toLower(e.description) CONTAINS toLower($query)
                OPTIONAL MATCH (e)-[:MENTIONED_IN|RELATED_TO]->(d:Document)
                RETURN e.name AS entity_name,
                       e.entity_type AS entity_type,
                       d.document_id AS document_id,
                       d.title AS document_title,
                       d.chunk_text AS chunk_text
                LIMIT $limit
            """
            records = await self._neo4j.run_query(
                cypher, parameters={"query": query, "limit": limit}
            )

            if not records:
                logger.info("Graph search returned 0 results (or Neo4j not ready)")
                return []

            items: List[SearchResultItem] = []
            for idx, record in enumerate(records):
                r = record if isinstance(record, dict) else dict(record) if record else {}
                score = 0.7 - (idx * 0.02)
                score = max(score, 0.1)

                entity_briefs: List[EntityBrief] = []
                if r.get("entity_name"):
                    try:
                        from shared.enums import EntityType
                        etype = r.get("entity_type", "equipment")
                        entity_briefs.append(
                            EntityBrief(
                                id=r.get("entity_name", ""),
                                entity_type=EntityType(etype) if etype else EntityType.EQUIPMENT,
                                name=r.get("entity_name", ""),
                            )
                        )
                    except (ValueError, KeyError):
                        pass

                items.append(
                    SearchResultItem(
                        document_id=r.get("document_id", ""),
                        chunk_text=r.get("chunk_text", ""),
                        relevance_score=score,
                        document_title=r.get("document_title", "Unknown"),
                        highlights=[],
                        entities=entity_briefs,
                    )
                )

            logger.info("Graph search returned %d results", len(items))
            return items

        except Exception as exc:
            logger.warning("Graph search failed (Neo4j may be unavailable): %s", exc)
            return []

    # ─── Hybrid Search ───────────────────────────────────

    async def hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[SearchResultItem]:
        """Combine results from semantic, keyword, and graph search
        using Reciprocal Rank Fusion (RRF).

        RRF formula: score = Σ 1 / (k + rank_i)  where k = 60.

        Args:
            query: The search query string.
            filters: Optional metadata filter dict.
            limit: Maximum number of results.

        Returns:
            Deduplicated, RRF-ranked list of SearchResultItem.
        """
        # Fan out to all three search methods concurrently
        sem_task = asyncio.create_task(
            self.semantic_search(query, filters, limit)
        )
        kw_task = asyncio.create_task(
            self.keyword_search(query, filters, limit)
        )
        graph_task = asyncio.create_task(
            self.graph_search(query, filters, limit)
        )

        semantic_results, keyword_results, graph_results = await asyncio.gather(
            sem_task, kw_task, graph_task
        )

        # Apply RRF scoring
        rrf_scores: Dict[str, float] = {}
        rrf_items: Dict[str, SearchResultItem] = {}

        for result_list in [semantic_results, keyword_results, graph_results]:
            for rank, item in enumerate(result_list):
                key = self._dedup_key(item)
                rrf_score = 1.0 / (_RRF_K + rank + 1)

                if key in rrf_scores:
                    rrf_scores[key] += rrf_score
                    # Keep the item with the higher original relevance score
                    if item.relevance_score > rrf_items[key].relevance_score:
                        rrf_items[key] = item
                else:
                    rrf_scores[key] = rrf_score
                    rrf_items[key] = item

        # Sort by RRF score descending
        sorted_keys = sorted(rrf_scores, key=rrf_scores.get, reverse=True)

        # Normalise RRF scores to [0, 1]
        if sorted_keys:
            max_score = rrf_scores[sorted_keys[0]]
            if max_score > 0:
                for key in sorted_keys:
                    rrf_scores[key] /= max_score

        results: List[SearchResultItem] = []
        for key in sorted_keys[:limit]:
            item = rrf_items[key]
            # Replace the original relevance with the normalised RRF score
            results.append(
                SearchResultItem(
                    document_id=item.document_id,
                    chunk_text=item.chunk_text,
                    relevance_score=round(rrf_scores[key], 4),
                    document_title=item.document_title,
                    document_category=item.document_category,
                    page_number=item.page_number,
                    highlights=item.highlights,
                    entities=item.entities,
                )
            )

        logger.info(
            "Hybrid search: semantic=%d keyword=%d graph=%d → merged=%d",
            len(semantic_results),
            len(keyword_results),
            len(graph_results),
            len(results),
        )
        return results

    # ─── Helpers ─────────────────────────────────────────

    @staticmethod
    def _build_search_result_item(
        raw: Dict[str, Any],
    ) -> SearchResultItem:
        """Convert a raw result dict to a SearchResultItem.

        Args:
            raw: Dictionary from embedding service search_similar.

        Returns:
            A populated SearchResultItem.
        """
        entity_briefs: List[EntityBrief] = []
        for ent in raw.get("entities", []):
            if isinstance(ent, dict):
                try:
                    entity_briefs.append(EntityBrief(**ent))
                except Exception:
                    pass

        return SearchResultItem(
            document_id=raw.get("document_id", ""),
            chunk_text=raw.get("chunk_text", ""),
            relevance_score=float(raw.get("relevance_score", 0.0)),
            document_title=raw.get("document_title", "Unknown"),
            document_category=raw.get("document_category"),
            page_number=raw.get("page_number"),
            highlights=[raw.get("chunk_text", "")[:100]] if raw.get("chunk_text") else [],
            entities=entity_briefs,
        )

    @staticmethod
    def _dedup_key(item: SearchResultItem) -> str:
        """Generate a deduplication key for a search result.

        Uses a combination of document_id and chunk_text hash.

        Args:
            item: The search result item.

        Returns:
            A string key for deduplication.
        """
        import hashlib
        text_hash = hashlib.md5(
            item.chunk_text.encode("utf-8", errors="replace")
        ).hexdigest()[:12]
        return f"{item.document_id}:{text_hash}"

    @staticmethod
    def _extract_highlights(
        text: str, query: str, window: int = 80
    ) -> List[str]:
        """Extract highlighted snippets around query matches.

        Args:
            text: The full chunk text.
            query: The search query.
            window: Characters of context around the match.

        Returns:
            List of highlight strings.
        """
        highlights: List[str] = []
        text_lower = text.lower()
        query_lower = query.lower()

        # Search for individual query words
        for word in query_lower.split():
            idx = text_lower.find(word)
            if idx >= 0:
                start = max(0, idx - window // 2)
                end = min(len(text), idx + len(word) + window // 2)
                snippet = text[start:end].strip()
                if snippet and snippet not in highlights:
                    highlights.append(f"…{snippet}…" if start > 0 else f"{snippet}…")

        return highlights[:3]  # Return at most 3 highlights

    @staticmethod
    def _normalize_scores(
        results: List[SearchResultItem],
    ) -> List[SearchResultItem]:
        """Normalize relevance scores to the [0, 1] range.

        Args:
            results: List of search results.

        Returns:
            The same list with normalised scores.
        """
        if not results:
            return results

        max_score = max(r.relevance_score for r in results)
        min_score = min(r.relevance_score for r in results)
        score_range = max_score - min_score

        if score_range == 0:
            return results

        normalised: List[SearchResultItem] = []
        for r in results:
            norm_score = (r.relevance_score - min_score) / score_range
            normalised.append(
                SearchResultItem(
                    document_id=r.document_id,
                    chunk_text=r.chunk_text,
                    relevance_score=round(norm_score, 4),
                    document_title=r.document_title,
                    document_category=r.document_category,
                    page_number=r.page_number,
                    highlights=r.highlights,
                    entities=r.entities,
                )
            )
        return normalised


# Module-level singleton
search_service = SearchService()
