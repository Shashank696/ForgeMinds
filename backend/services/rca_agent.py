"""
ForgeMinds — Root Cause Analysis Agent.

Specialised agent for systematic failure investigation using 5-Why
methodology, fishbone analysis, and pattern matching against historical
incidents.  Identifies ranked root causes with confidence levels,
evidence citations, and corrective/preventive action recommendations.
"""

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.utils.logger import get_logger
from shared.enums import AgentType, RiskLevel
from shared.interfaces import (
    ChatResponse,
    Citation,
    EquipmentBrief,
    IncidentBrief,
    RCARequest,
    RCAResponse,
    RootCause,
)

logger = get_logger(__name__)


class RCAAgent:
    """Specialised agent for Root Cause Analysis.

    Provides systematic failure investigation with ranked root causes,
    similar incident discovery, and cross-equipment failure correlation.
    """

    def __init__(self) -> None:
        """Initialise with lazy references to shared services."""
        self._rag = None  # Lazy — avoids circular import
        self._db = db
        logger.info("RCAAgent initialised")

    def _get_rag(self):
        """Lazy import of RAGService to avoid circular dependencies."""
        if self._rag is None:
            from backend.services.rag_service import rag_service
            self._rag = rag_service
        return self._rag

    # ─── Root Cause Analysis ─────────────────────────────

    async def analyze_root_cause(
        self, request: RCARequest
    ) -> RCAResponse:
        """Perform root cause analysis for an equipment failure.

        Searches for similar historical failures, analyzes maintenance
        history, and uses LLM with structured 5-Why / fishbone prompting
        to identify probable root causes.

        Args:
            request: RCARequest containing equipment_id, failure_description,
                     and optional failure_date.

        Returns:
            RCAResponse with ranked root causes, recommendations, and
            related at-risk equipment.
        """
        try:
            rag = self._get_rag()
            equipment_id = request.equipment_id
            failure_desc = request.failure_description

            # Retrieve context about this failure
            rca_query = (
                f"Root cause analysis for equipment {equipment_id}: "
                f"{failure_desc}. What are the possible causes, contributing "
                f"factors, and historical precedents?"
            )
            context = await rag.retrieve_context(query=rca_query, limit=12)

            # Find similar historical incidents
            similar_incidents = await self.find_similar_incidents(failure_desc)

            # Generate structured RCA via LLM
            rca_prompt = (
                f"Perform a root cause analysis for the following failure:\n\n"
                f"Equipment ID: {equipment_id}\n"
                f"Failure Description: {failure_desc}\n"
                f"Failure Date: {request.failure_date or 'Not specified'}\n\n"
                f"Use the 5-Why methodology and fishbone analysis approach. "
                f"Identify the top root causes ranked by likelihood. "
                f"For each root cause, provide:\n"
                f"1. The cause description\n"
                f"2. Confidence level (0.0 to 1.0)\n"
                f"3. Supporting evidence from the documents\n"
                f"4. Recommended corrective and preventive actions\n"
            )

            response = await rag.generate_response(
                query=rca_prompt,
                context=context,
                agent_type=AgentType.RCA,
            )

            # Build structured root causes from context and LLM response
            root_causes: List[RootCause] = []

            # Primary root cause from LLM analysis
            primary_evidence: List[Citation] = []
            for chunk in context[:3]:
                primary_evidence.append(Citation(
                    document_id=chunk.get("document_id", ""),
                    document_title=chunk.get("document_title", "Unknown"),
                    chunk_text=chunk.get("chunk_text", "")[:300],
                    page_number=chunk.get("page_number"),
                    relevance_score=float(chunk.get("relevance_score", 0.5)),
                ))

            root_causes.append(RootCause(
                cause=response.response[:500] if response.response else "Analysis in progress",
                confidence=response.confidence_score,
                evidence=primary_evidence,
                similar_incidents=similar_incidents[:3],
            ))

            # Secondary root causes based on context patterns
            if len(context) > 3:
                for idx, chunk in enumerate(context[3:6], start=2):
                    root_causes.append(RootCause(
                        cause=f"Contributing factor {idx}: {chunk.get('chunk_text', '')[:200]}",
                        confidence=max(0.3, float(chunk.get("relevance_score", 0.3)) - 0.2),
                        evidence=[Citation(
                            document_id=chunk.get("document_id", ""),
                            document_title=chunk.get("document_title", "Unknown"),
                            chunk_text=chunk.get("chunk_text", "")[:300],
                            page_number=chunk.get("page_number"),
                            relevance_score=float(chunk.get("relevance_score", 0.3)),
                        )],
                        similar_incidents=[],
                    ))

            # Recommended actions
            recommended_actions = [
                "Investigate the identified root causes through physical inspection",
                "Review maintenance records for the affected equipment",
                "Implement corrective actions as recommended by the analysis",
                "Update preventive maintenance procedures to address identified gaps",
                "Share findings as lessons learned with operations team",
            ]

            # Find related at-risk equipment
            related_equipment = await self.correlate_failures(equipment_id)

            rca_response = RCAResponse(
                root_causes=root_causes,
                recommended_actions=recommended_actions,
                related_equipment_at_risk=related_equipment,
            )

            logger.info(
                "RCA completed for equipment %s: %d root causes identified",
                equipment_id,
                len(root_causes),
            )
            return rca_response

        except Exception as exc:
            logger.error("Root cause analysis failed: %s", exc)
            return RCAResponse(
                root_causes=[
                    RootCause(
                        cause=f"Analysis could not be completed: {exc}",
                        confidence=0.0,
                        evidence=[],
                        similar_incidents=[],
                    )
                ],
                recommended_actions=["Retry the analysis or investigate manually"],
                related_equipment_at_risk=[],
            )

    # ─── Similar Incidents ───────────────────────────────

    async def find_similar_incidents(
        self, failure_description: str
    ) -> List[IncidentBrief]:
        """Find historically similar incidents via semantic search.

        Args:
            failure_description: Description of the current failure.

        Returns:
            List of IncidentBrief objects for similar past incidents.
        """
        try:
            rag = self._get_rag()
            context = await rag.retrieve_context(
                query=f"similar incident: {failure_description}",
                filters={"document_category": "incident_report"},
                limit=5,
            )

            incidents: List[IncidentBrief] = []
            for chunk in context:
                incidents.append(IncidentBrief(
                    id=chunk.get("document_id", str(uuid.uuid4())),
                    description=chunk.get("chunk_text", "")[:200],
                    date=date.today(),  # Actual date would come from metadata
                    equipment_tag=chunk.get("document_title", "Unknown"),
                    severity="medium",
                ))

            logger.info(
                "Found %d similar incidents for '%s'",
                len(incidents),
                failure_description[:60],
            )
            return incidents

        except Exception as exc:
            logger.warning("Similar incident search failed: %s", exc)
            return []

    # ─── Failure Correlation ─────────────────────────────

    async def correlate_failures(
        self, equipment_id: str
    ) -> List[EquipmentBrief]:
        """Find related equipment with similar failure patterns.

        Uses knowledge graph relationships to identify equipment in the
        same system, with shared components, or exhibiting similar
        degradation patterns.

        Args:
            equipment_id: The equipment identifier.

        Returns:
            List of EquipmentBrief for related at-risk equipment.
        """
        try:
            from backend.db.neo4j_client import neo4j_db
            from shared.enums import Criticality, EquipmentType

            cypher = """
                MATCH (e1 {equipment_id: $equipment_id})-[:PART_OF|CONNECTED_TO|SAME_SYSTEM]-(e2)
                RETURN e2.equipment_id AS id,
                       e2.tag AS tag,
                       e2.name AS name,
                       e2.equipment_type AS equipment_type,
                       e2.criticality AS criticality
                LIMIT 5
            """
            records = await neo4j_db.run_query(
                cypher, parameters={"equipment_id": equipment_id}
            )

            if not records:
                return []

            related: List[EquipmentBrief] = []
            for record in records:
                r = record if isinstance(record, dict) else dict(record) if record else {}
                try:
                    related.append(EquipmentBrief(
                        id=r.get("id", ""),
                        tag=r.get("tag", ""),
                        name=r.get("name", ""),
                        equipment_type=EquipmentType(r.get("equipment_type", "other")),
                        criticality=Criticality(r.get("criticality", "medium")),
                    ))
                except (ValueError, KeyError):
                    pass

            return related

        except Exception as exc:
            logger.warning("Failure correlation failed: %s", exc)
            return []

    # ─── Query Processing ────────────────────────────────

    async def process_query(
        self,
        query: str,
        context_filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> ChatResponse:
        """Handle RCA-specific queries via RAG.

        Args:
            query: The user query.
            context_filters: Optional filters for context retrieval.
            session_id: Optional session identifier.

        Returns:
            A ChatResponse with RCA-tuned answer.
        """
        rag = self._get_rag()
        context = await rag.retrieve_context(
            query=query, filters=context_filters, limit=10
        )
        return await rag.generate_response(
            query=query,
            context=context,
            agent_type=AgentType.RCA,
            session_id=session_id,
        )


# Module-level singleton
rca_agent = RCAAgent()
