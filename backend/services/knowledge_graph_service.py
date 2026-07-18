"""
ForgeMinds — Knowledge Graph Service.
CRUD and query operations over Neo4j for the industrial knowledge graph.
Assigned to: RUDRA
"""

import uuid
from typing import List, Dict, Any, Optional

from shared.enums import EntityType
from shared.interfaces import (
    GraphNode, GraphEdge, SubgraphResponse, KGStatsResponse, EntityBrief,
)
from shared.constants import MAX_GRAPH_DEPTH, MAX_GRAPH_NODES
from backend.db.neo4j_client import neo4j_db
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Mapping from EntityType enum values to Neo4j node labels
_LABEL_MAP: Dict[str, str] = {
    "equipment": "Equipment",
    "document": "Document",
    "person": "Person",
    "procedure": "Procedure",
    "regulation": "Regulation",
    "failure_event": "FailureEvent",
    "maintenance_action": "MaintenanceAction",
    "location": "Location",
    "parameter": "Parameter",
    "part": "Part",
}


class KnowledgeGraphService:
    """Handles Knowledge Graph operations. Assigned to: RUDRA"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.neo4j = neo4j_db

    # ──────────────────────────────────────────────
    # Node operations
    # ──────────────────────────────────────────────

    async def create_node(self, node_data: dict) -> str:
        """
        Create or merge a node. Uses MERGE by (name, label) to prevent duplicates.

        Args:
            node_data: {name, entity_type, properties, [id]}

        Returns:
            The node id (existing or newly created).
        """
        name = node_data.get("name", "")
        entity_type = node_data.get("entity_type", "equipment")
        label = self._entity_type_to_label(entity_type)
        node_id = node_data.get("id", str(uuid.uuid4()))
        properties = node_data.get("properties", {})

        # Build flat property map for SET
        props = {
            "id": node_id,
            "name": name,
            "entity_type": entity_type,
            **{k: v for k, v in properties.items() if isinstance(v, (str, int, float, bool))},
        }

        query = (
            f"MERGE (n:{label} {{name: $name}}) "
            f"ON CREATE SET n += $props "
            f"ON MATCH SET n.entity_type = $entity_type "
            f"RETURN n.id AS id"
        )
        try:
            records = await self.neo4j.run_write_query(
                query,
                {"name": name, "props": props, "entity_type": entity_type},
            )
            result_id = records[0]["id"] if records else node_id
            self.logger.debug("Created/merged node: %s (%s)", name, label)
            return result_id
        except Exception as exc:
            self.logger.error("create_node failed for %s: %s", name, exc)
            raise

    async def create_edge(self, source_id: str, target_id: str, rel_data: dict) -> bool:
        """
        Create a relationship between two nodes.

        Args:
            source_id: Source node id.
            target_id: Target node id.
            rel_data: {relationship_type, [confidence], [properties]}
        """
        rel_type = rel_data.get("relationship_type", "REFERENCES").upper()
        confidence = rel_data.get("confidence", 1.0)
        props = rel_data.get("properties", {})
        props["confidence"] = confidence
        rel_id = str(uuid.uuid4())
        props["id"] = rel_id

        query = (
            f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
            f"CREATE (a)-[r:{rel_type} $props]->(b) "
            f"RETURN type(r) AS type"
        )
        try:
            records = await self.neo4j.run_write_query(
                query,
                {"source_id": source_id, "target_id": target_id, "props": props},
            )
            created = len(records) > 0
            if created:
                self.logger.debug("Created edge %s -> %s [%s]", source_id[:8], target_id[:8], rel_type)
            return created
        except Exception as exc:
            self.logger.error("create_edge failed: %s", exc)
            return False

    # ──────────────────────────────────────────────
    # Query operations
    # ──────────────────────────────────────────────

    async def get_node(self, node_id: str) -> Optional[dict]:
        """Retrieve a single node by ID, with connection count."""
        query = (
            "MATCH (n {id: $node_id}) "
            "OPTIONAL MATCH (n)-[r]-() "
            "RETURN n, count(r) AS connection_count"
        )
        try:
            records = await self.neo4j.run_query(query, {"node_id": node_id})
            if not records:
                return None
            rec = records[0]
            n = rec.get("n", {})
            return {
                "id": n.get("id", node_id),
                "entity_type": n.get("entity_type", "equipment"),
                "name": n.get("name", ""),
                "properties": {k: v for k, v in n.items() if k not in ("id", "entity_type", "name")},
                "connection_count": rec.get("connection_count", 0),
            }
        except Exception as exc:
            self.logger.error("get_node failed for %s: %s", node_id, exc)
            raise

    async def get_subgraph(self, node_id: str, depth: int = 2) -> dict:
        """Get subgraph around a focal node up to given depth."""
        depth = min(depth, MAX_GRAPH_DEPTH)

        query = (
            "MATCH (n {id: $node_id}) "
            f"OPTIONAL MATCH path = (n)-[*1..{depth}]-(m) "
            "WITH n, collect(DISTINCT m) AS connected, "
            "collect(DISTINCT relationships(path)) AS all_rels "
            "RETURN n, connected, all_rels "
            f"LIMIT {MAX_GRAPH_NODES}"
        )
        try:
            records = await self.neo4j.run_query(query, {"node_id": node_id})
            nodes_map: Dict[str, dict] = {}
            edges_list: List[dict] = []

            for rec in records:
                # Focal node
                focal = rec.get("n", {})
                if focal:
                    fid = focal.get("id", node_id)
                    nodes_map[fid] = self._node_to_dict(focal)

                # Connected nodes
                for m in (rec.get("connected") or []):
                    if m:
                        mid = m.get("id", "")
                        if mid and mid not in nodes_map:
                            nodes_map[mid] = self._node_to_dict(m)

                # Relationships
                for rel_list in (rec.get("all_rels") or []):
                    if rel_list:
                        for r in rel_list:
                            if r:
                                edges_list.append(self._rel_to_dict(r))

            # Deduplicate edges
            seen_edges: set = set()
            unique_edges: List[dict] = []
            for e in edges_list:
                key = (e.get("source_id", ""), e.get("target_id", ""), e.get("relationship_type", ""))
                if key not in seen_edges:
                    seen_edges.add(key)
                    unique_edges.append(e)

            return {
                "nodes": list(nodes_map.values()),
                "edges": unique_edges,
            }
        except Exception as exc:
            self.logger.error("get_subgraph failed for %s: %s", node_id, exc)
            return {"nodes": [], "edges": []}

    async def get_stats(self) -> dict:
        """Get aggregate knowledge graph statistics."""
        try:
            # Count nodes by label
            node_records = await self.neo4j.run_query(
                "MATCH (n) RETURN labels(n) AS labels, count(n) AS cnt"
            )
            nodes_by_type: Dict[str, int] = {}
            total_nodes = 0
            for rec in node_records:
                labels = rec.get("labels", [])
                cnt = rec.get("cnt", 0)
                label = labels[0] if labels else "Unknown"
                nodes_by_type[label] = nodes_by_type.get(label, 0) + cnt
                total_nodes += cnt

            # Count edges by type
            edge_records = await self.neo4j.run_query(
                "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS cnt"
            )
            edges_by_type: Dict[str, int] = {}
            total_edges = 0
            for rec in edge_records:
                rt = rec.get("rel_type", "UNKNOWN")
                cnt = rec.get("cnt", 0)
                edges_by_type[rt] = cnt
                total_edges += cnt

            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "nodes_by_type": nodes_by_type,
                "edges_by_type": edges_by_type,
            }
        except Exception as exc:
            self.logger.error("get_stats failed: %s", exc)
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "nodes_by_type": {},
                "edges_by_type": {},
            }

    async def search_nodes(
        self,
        query: str = "",
        entity_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[dict]:
        """Search nodes by name, with optional type filter."""
        limit = min(limit, MAX_GRAPH_NODES)

        if entity_type:
            label = self._entity_type_to_label(entity_type)
            cypher = (
                f"MATCH (n:{label}) WHERE toLower(n.name) CONTAINS toLower($query) "
                f"OPTIONAL MATCH (n)-[r]-() "
                f"RETURN n, count(r) AS connection_count "
                f"ORDER BY n.name LIMIT $limit"
            )
        elif query:
            cypher = (
                "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($query) "
                "OPTIONAL MATCH (n)-[r]-() "
                "RETURN n, count(r) AS connection_count "
                "ORDER BY n.name LIMIT $limit"
            )
        else:
            cypher = (
                "MATCH (n) "
                "OPTIONAL MATCH (n)-[r]-() "
                "RETURN n, count(r) AS connection_count "
                "ORDER BY n.name LIMIT $limit"
            )

        try:
            records = await self.neo4j.run_query(cypher, {"query": query or "", "limit": limit})
            return [
                {
                    "id": rec.get("n", {}).get("id", ""),
                    "entity_type": rec.get("n", {}).get("entity_type", "equipment"),
                    "name": rec.get("n", {}).get("name", ""),
                    "properties": {
                        k: v for k, v in rec.get("n", {}).items()
                        if k not in ("id", "entity_type", "name")
                    },
                    "connection_count": rec.get("connection_count", 0),
                }
                for rec in records
            ]
        except Exception as exc:
            self.logger.error("search_nodes failed: %s", exc)
            return []

    async def link_entities(
        self,
        document_id: str,
        entities: list,
        relationships: Optional[list] = None,
    ) -> dict:
        """
        Batch-create nodes and edges from entity extraction results.

        Creates a Document node, entity nodes, REFERENCES edges, and
        any additional extracted relationships.
        """
        nodes_created = 0
        edges_created = 0

        # 1. Create Document node
        doc_node_id = await self.create_node({
            "id": document_id,
            "name": f"Document-{document_id[:8]}",
            "entity_type": "document",
            "properties": {"source": "ingestion_pipeline"},
        })
        nodes_created += 1

        # 2. Create entity nodes + REFERENCES edges
        entity_id_map: Dict[str, str] = {}  # original_id -> neo4j_id
        for entity in entities:
            e_name = entity.name if isinstance(entity, EntityBrief) else entity.get("name", "")
            e_type = (entity.entity_type.value if isinstance(entity, EntityBrief)
                      else entity.get("entity_type", "equipment"))
            e_id = entity.id if isinstance(entity, EntityBrief) else entity.get("id", str(uuid.uuid4()))
            e_props = entity.properties if isinstance(entity, EntityBrief) else entity.get("properties", {})

            neo_id = await self.create_node({
                "id": e_id,
                "name": e_name,
                "entity_type": e_type,
                "properties": e_props,
            })
            entity_id_map[e_id] = neo_id
            nodes_created += 1

            # Create REFERENCES edge from document to entity
            created = await self.create_edge(doc_node_id, neo_id, {
                "relationship_type": "REFERENCES",
                "confidence": e_props.get("confidence", 0.8) if isinstance(e_props, dict) else 0.8,
            })
            if created:
                edges_created += 1

        # 3. Create extracted relationships
        if relationships:
            for rel in relationships:
                src_id = entity_id_map.get(rel.get("source_entity_id", ""), rel.get("source_entity_id", ""))
                tgt_id = entity_id_map.get(rel.get("target_entity_id", ""), rel.get("target_entity_id", ""))
                created = await self.create_edge(src_id, tgt_id, {
                    "relationship_type": rel.get("relationship_type", "REFERENCES"),
                    "confidence": rel.get("confidence", 0.75),
                    "properties": {"source_document_id": rel.get("source_document_id", document_id)},
                })
                if created:
                    edges_created += 1

        self.logger.info(
            "Linked %d nodes, %d edges for document %s",
            nodes_created, edges_created, document_id[:8],
        )
        return {"nodes_created": nodes_created, "edges_created": edges_created}

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _entity_type_to_label(entity_type: str) -> str:
        """Map EntityType enum value to Neo4j node label."""
        if isinstance(entity_type, EntityType):
            entity_type = entity_type.value
        return _LABEL_MAP.get(entity_type, "Entity")

    @staticmethod
    def _node_to_dict(n: dict) -> dict:
        return {
            "id": n.get("id", ""),
            "entity_type": n.get("entity_type", "equipment"),
            "name": n.get("name", ""),
            "properties": {k: v for k, v in n.items() if k not in ("id", "entity_type", "name")},
            "connection_count": 0,
        }

    @staticmethod
    def _rel_to_dict(r) -> dict:
        """Convert a neo4j relationship object or dict to edge dict."""
        if hasattr(r, "type"):
            # neo4j.graph.Relationship object
            return {
                "id": dict(r).get("id", str(uuid.uuid4())),
                "source_id": dict(r.start_node).get("id", "") if hasattr(r, "start_node") else "",
                "target_id": dict(r.end_node).get("id", "") if hasattr(r, "end_node") else "",
                "relationship_type": r.type,
                "properties": dict(r),
                "confidence": dict(r).get("confidence", 1.0),
            }
        # dict fallback
        return {
            "id": r.get("id", str(uuid.uuid4())),
            "source_id": r.get("source_id", ""),
            "target_id": r.get("target_id", ""),
            "relationship_type": r.get("relationship_type", r.get("type", "REFERENCES")),
            "properties": r.get("properties", {}),
            "confidence": r.get("confidence", 1.0),
        }
