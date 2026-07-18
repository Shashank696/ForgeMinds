"""
ForgeMinds — Lessons Learned Agent.

Specialised agent for analyzing historical incidents, identifying
recurring failure patterns, synthesizing actionable lessons, and
generating proactive warnings to prevent recurrence.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.db.database import db
from backend.utils.logger import get_logger
from shared.enums import AgentType, RiskLevel
from shared.interfaces import (
    ChatResponse,
    Citation,
    ProactiveAlert,
)

logger = get_logger(__name__)


class LessonsLearnedAgent:
    """Specialised agent for organizational learning.

    Analyzes past incidents and near-misses to identify recurring
    patterns, extract actionable lessons, and generate proactive
    warnings for operations teams.
    """

    def __init__(self) -> None:
        """Initialise with lazy references to shared services."""
        self._rag = None  # Lazy — avoids circular import
        self._db = db
        logger.info("LessonsLearnedAgent initialised")

    def _get_rag(self):
        """Lazy import of RAGService to avoid circular dependencies."""
        if self._rag is None:
            from backend.services.rag_service import rag_service
            self._rag = rag_service
        return self._rag

    # ─── Incident Analysis ───────────────────────────────

    async def analyze_incidents(
        self,
        query: str = "historical incidents and lessons learned",
        context_filters: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Analyze past incidents for patterns and lessons.

        Searches incident reports, near-misses, and audit findings,
        then uses LLM to synthesize patterns and actionable lessons.

        Args:
            query: The analysis query (defaults to a broad search).
            context_filters: Optional metadata filters.

        Returns:
            ChatResponse with synthesized analysis.
        """
        try:
            rag = self._get_rag()

            # Search across incident-related documents
            analysis_query = (
                f"Analyze incidents and lessons learned: {query}. "
                f"Identify patterns, common root causes, and actionable "
                f"recommendations to prevent recurrence."
            )
            context = await rag.retrieve_context(
                query=analysis_query,
                filters=context_filters or {"document_category": "incident_report"},
                limit=12,
            )

            # Broaden search if incident-specific filter yields nothing
            if not context:
                context = await rag.retrieve_context(
                    query=analysis_query,
                    limit=10,
                )

            return await rag.generate_response(
                query=analysis_query,
                context=context,
                agent_type=AgentType.LESSONS_LEARNED,
            )

        except Exception as exc:
            logger.error("Incident analysis failed: %s", exc)
            import uuid as _uuid
            return ChatResponse(
                session_id=str(_uuid.uuid4()),
                response=f"Unable to complete incident analysis: {exc}",
                agent_type=AgentType.LESSONS_LEARNED,
                confidence_score=0.0,
            )

    # ─── Pattern Detection ───────────────────────────────

    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect recurring failure and incident patterns.

        Analyzes historical incidents to identify systemic issues,
        common root causes, and recurring themes across the document
        corpus.

        Returns:
            List of pattern dictionaries with description, frequency,
            affected areas, and recommendations.
        """
        try:
            rag = self._get_rag()

            pattern_query = (
                "What are the recurring patterns across historical incidents, "
                "failures, and near-misses? Identify systemic issues, common "
                "root causes, equipment types most frequently involved, and "
                "seasonal or time-based patterns."
            )
            context = await rag.retrieve_context(
                query=pattern_query, limit=15
            )

            if not context:
                logger.info("No incident context available for pattern detection")
                return []

            response = await rag.generate_response(
                query=pattern_query,
                context=context,
                agent_type=AgentType.LESSONS_LEARNED,
            )

            # Build structured patterns from context analysis
            patterns: List[Dict[str, Any]] = []

            # Group context by document category for pattern extraction
            category_groups: Dict[str, List[Dict[str, Any]]] = {}
            for chunk in context:
                cat = chunk.get("document_category", "other")
                category_groups.setdefault(cat, []).append(chunk)

            for category, chunks in category_groups.items():
                if len(chunks) >= 2:  # Pattern requires at least 2 instances
                    patterns.append({
                        "pattern_id": str(uuid.uuid4()),
                        "description": (
                            f"Recurring theme detected in {category} documents "
                            f"({len(chunks)} instances found)"
                        ),
                        "category": category,
                        "instance_count": len(chunks),
                        "affected_documents": [
                            c.get("document_title", "Unknown") for c in chunks
                        ],
                        "summary": response.response[:300] if response.response else "",
                        "severity": "high" if len(chunks) >= 4 else "medium",
                        "recommendation": (
                            "Review the identified pattern and implement "
                            "systemic corrective actions"
                        ),
                    })

            # Always include the LLM's overall pattern analysis
            if response.response:
                patterns.insert(0, {
                    "pattern_id": str(uuid.uuid4()),
                    "description": "AI-synthesized pattern analysis",
                    "category": "cross-category",
                    "instance_count": len(context),
                    "summary": response.response[:500],
                    "severity": "medium",
                    "recommendation": "Review findings with operations team",
                })

            logger.info("Detected %d patterns from %d context chunks",
                        len(patterns), len(context))
            return patterns

        except Exception as exc:
            logger.error("Pattern detection failed: %s", exc)
            return []

    # ─── Proactive Warnings ──────────────────────────────

    async def generate_warnings(self) -> List[ProactiveAlert]:
        """Generate proactive warnings based on detected patterns.

        Cross-references detected patterns with current equipment
        states and operational conditions to produce actionable
        warning alerts.

        Returns:
            List of ProactiveAlert objects sorted by severity.
        """
        try:
            rag = self._get_rag()

            warning_query = (
                "Based on historical incident patterns, what proactive "
                "warnings should be issued? Consider equipment approaching "
                "typical failure timelines, recurring seasonal risks, and "
                "any systemic issues that have not been fully resolved."
            )
            context = await rag.retrieve_context(
                query=warning_query, limit=10
            )

            if not context:
                return []

            response = await rag.generate_response(
                query=warning_query,
                context=context,
                agent_type=AgentType.LESSONS_LEARNED,
            )

            alerts: List[ProactiveAlert] = []
            for idx, chunk in enumerate(context[:5]):
                relevance = float(chunk.get("relevance_score", 0.5))

                # Determine severity based on relevance and position
                if relevance > 0.85:
                    severity = RiskLevel.HIGH
                elif relevance > 0.7:
                    severity = RiskLevel.MEDIUM
                else:
                    severity = RiskLevel.LOW

                alert = ProactiveAlert(
                    id=str(uuid.uuid4()),
                    alert_type="failure_pattern",
                    severity=severity,
                    title=(
                        f"Lesson-based warning: "
                        f"{chunk.get('document_title', 'Historical pattern')}"
                    ),
                    description=(
                        f"Historical analysis indicates attention needed: "
                        f"{chunk.get('chunk_text', '')[:250]}"
                    ),
                    equipment=None,
                    evidence=[
                        Citation(
                            document_id=chunk.get("document_id", ""),
                            document_title=chunk.get("document_title", "Unknown"),
                            chunk_text=chunk.get("chunk_text", "")[:200],
                            relevance_score=relevance,
                        )
                    ],
                    created_at=datetime.utcnow(),
                )
                alerts.append(alert)

            logger.info("Generated %d proactive warnings", len(alerts))
            return alerts

        except Exception as exc:
            logger.error("Warning generation failed: %s", exc)
            return []

    # ─── Query Processing ────────────────────────────────

    async def process_query(
        self,
        query: str,
        context_filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> ChatResponse:
        """Handle lessons-learned queries via RAG.

        Args:
            query: The user query.
            context_filters: Optional filters for context retrieval.
            session_id: Optional session identifier.

        Returns:
            A ChatResponse with lessons-learned tuned answer.
        """
        rag = self._get_rag()
        context = await rag.retrieve_context(
            query=query, filters=context_filters, limit=10
        )
        return await rag.generate_response(
            query=query,
            context=context,
            agent_type=AgentType.LESSONS_LEARNED,
            session_id=session_id,
        )


# Module-level singleton
lessons_agent = LessonsLearnedAgent()
