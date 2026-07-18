"""
ForgeMinds — Knowledge Graph API.
Endpoints for node listing, retrieval, subgraph queries, and stats.
Assigned to: RUDRA
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from shared.interfaces import GraphNode, SubgraphResponse, KGStatsResponse
from backend.services.knowledge_graph_service import KnowledgeGraphService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/knowledge-graph", tags=['Knowledge Graph'])

kg_service = KnowledgeGraphService()


@router.get("/nodes", response_model=List[GraphNode])
async def list_nodes(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
):
    """Assigned to: RUDRA"""
    try:
        results = await kg_service.search_nodes(
            query=search or "", entity_type=entity_type, limit=limit,
        )
        return [
            GraphNode(
                id=r["id"],
                entity_type=r.get("entity_type", "equipment"),
                name=r.get("name", ""),
                properties=r.get("properties", {}),
                connection_count=r.get("connection_count", 0),
            )
            for r in results
        ]
    except Exception as exc:
        logger.error("list_nodes failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list nodes",
        )


@router.get("/nodes/{node_id}", response_model=GraphNode)
async def get_node(node_id: str):
    """Assigned to: RUDRA"""
    try:
        result = await kg_service.get_node(node_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
        return GraphNode(
            id=result["id"],
            entity_type=result.get("entity_type", "equipment"),
            name=result.get("name", ""),
            properties=result.get("properties", {}),
            connection_count=result.get("connection_count", 0),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_node failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve node",
        )


@router.get("/subgraph/{node_id}", response_model=SubgraphResponse)
async def get_subgraph(node_id: str, depth: int = Query(2)):
    """Assigned to: RUDRA"""
    try:
        result = await kg_service.get_subgraph(node_id, depth)
        return SubgraphResponse(
            nodes=[
                GraphNode(
                    id=n["id"],
                    entity_type=n.get("entity_type", "equipment"),
                    name=n.get("name", ""),
                    properties=n.get("properties", {}),
                    connection_count=n.get("connection_count", 0),
                )
                for n in result.get("nodes", [])
            ],
            edges=[
                {
                    "id": e.get("id", ""),
                    "source_id": e.get("source_id", ""),
                    "target_id": e.get("target_id", ""),
                    "relationship_type": e.get("relationship_type", "REFERENCES"),
                    "properties": e.get("properties", {}),
                    "confidence": e.get("confidence", 1.0),
                }
                for e in result.get("edges", [])
            ],
        )
    except Exception as exc:
        logger.error("get_subgraph failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subgraph",
        )


@router.get("/stats", response_model=KGStatsResponse)
async def get_stats():
    """Assigned to: RUDRA"""
    try:
        stats = await kg_service.get_stats()
        return KGStatsResponse(
            total_nodes=stats.get("total_nodes", 0),
            total_edges=stats.get("total_edges", 0),
            nodes_by_type=stats.get("nodes_by_type", {}),
            edges_by_type=stats.get("edges_by_type", {}),
        )
    except Exception as exc:
        logger.error("get_stats failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )
