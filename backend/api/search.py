"""
Search API endpoint for the ForgeMinds knowledge search.

Routes queries to the appropriate search strategy (semantic, keyword,
graph, or hybrid) and returns ranked results with timing metadata.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from shared.interfaces import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    ErrorDetail,
    ErrorResponse,
)
from shared.enums import SearchType
from backend.services.search_service import search_service
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/search", tags=['Search'])


@router.post(
    "/",
    response_model=SearchResponse,
    responses={500: {"model": ErrorResponse}},
)
async def search(data: SearchRequest) -> SearchResponse:
    """Execute a search query across the ForgeMinds knowledge base.

    Routes the query to the appropriate search backend based on
    the requested search_type (SEMANTIC, KEYWORD, GRAPH, or HYBRID).
    Defaults to HYBRID when no type is specified.

    Args:
        data: The search request containing the query string,
              search_type, optional filters, and result limit.

    Returns:
        SearchResponse containing ranked results, total count,
        and search execution time in milliseconds.

    Raises:
        HTTPException: 500 if the search operation fails.
    """
    try:
        logger.info(
            "Search request — type=%s query='%s' limit=%d",
            data.search_type.value,
            data.query[:80],
            data.limit,
        )

        start_time = time.time()

        results: List[SearchResultItem] = await _dispatch_search(
            query=data.query,
            search_type=data.search_type,
            filters=data.filters,
            limit=data.limit,
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Search completed — type=%s results=%d time_ms=%d",
            data.search_type.value,
            len(results),
            elapsed_ms,
        )

        return SearchResponse(
            results=results,
            total_results=len(results),
            search_time_ms=elapsed_ms,
        )

    except NotImplementedError:
        logger.warning(
            "Search type '%s' is not yet implemented", data.search_type.value
        )
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message=f"Search type '{data.search_type.value}' is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error("Search endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="SEARCH_ERROR",
                message="An error occurred while executing the search.",
                details={"error": str(exc)},
            ).model_dump(),
        )


async def _dispatch_search(
    query: str,
    search_type: SearchType,
    filters: dict | None,
    limit: int,
) -> List[SearchResultItem]:
    """Route the search to the correct service method.

    Args:
        query: The search query string.
        search_type: The strategy to use for searching.
        filters: Optional filtering criteria.
        limit: Maximum number of results to return.

    Returns:
        List of SearchResultItem from the chosen search strategy.
    """
    if search_type == SearchType.SEMANTIC:
        return await search_service.semantic_search(
            query=query, filters=filters, limit=limit
        )
    elif search_type == SearchType.KEYWORD:
        return await search_service.keyword_search(
            query=query, filters=filters, limit=limit
        )
    elif search_type == SearchType.GRAPH:
        return await search_service.graph_search(
            query=query, filters=filters, limit=limit
        )
    else:
        # Default: HYBRID
        return await search_service.hybrid_search(
            query=query, filters=filters, limit=limit
        )
